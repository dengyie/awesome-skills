#!/usr/bin/env node
/**
 * Firecrawl key pool: resolution, round-robin rotation, per-key cooldown, and rotation on
 * quota exhaustion.
 */
import assert from "node:assert/strict";
import { mkdtemp, readFile, writeFile } from "node:fs/promises";
import { mkdtempSync, rmSync } from "node:fs";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import path from "node:path";
import { resolveFirecrawlApiKeys } from "../scripts/lib/config.js";
import { readFirecrawlCooldownState, recordFirecrawlCooldown } from "../scripts/lib/cooldown.js";
import {
  allFirecrawlKeys,
  firecrawlAuthMode,
  firecrawlChannelCooldown,
  firecrawlKeyFingerprint,
  firecrawlSearch,
  firecrawlScrape,
  hasFirecrawlApiKey,
  isFirecrawlKeySpentError,
  isFirecrawlQuotaError,
  loadFirecrawlRoundRobinIndex,
  nextFirecrawlApiKey,
  saveFirecrawlRoundRobinIndex,
} from "../scripts/lib/providers.js";

function noEnv() {
  return undefined;
}

// --- key resolution: the same precedence the Tavily pool uses ---

assert.deepEqual(
  resolveFirecrawlApiKeys({ firecrawlApiKeys: [], firecrawlApiKey: "fc-real" }, noEnv),
  ["fc-real"],
  "empty firecrawlApiKeys must not swallow firecrawlApiKey"
);
assert.deepEqual(resolveFirecrawlApiKeys({ firecrawlApiKey: "fc-real" }, noEnv), ["fc-real"]);
assert.deepEqual(
  resolveFirecrawlApiKeys({ firecrawlApiKeys: ["a", "b"], firecrawlApiKey: "c" }, noEnv),
  ["a", "b", "c"],
  "file multi + single merge"
);
assert.deepEqual(resolveFirecrawlApiKeys({ firecrawlApiKeys: ["a", "a", "b"] }, noEnv), ["a", "b"]);
assert.deepEqual(
  resolveFirecrawlApiKeys({}, (name) => (name === "FIRECRAWL_API_KEYS" ? "k1, k2, k1" : undefined)),
  ["k1", "k2"],
  "env multi wins and dedupes"
);
assert.deepEqual(
  resolveFirecrawlApiKeys({ firecrawlApiKeys: ["file"] }, (name) => (name === "FIRECRAWL_API_KEY" ? "env-single" : undefined)),
  ["env-single"],
  "single env key beats the file"
);
assert.deepEqual(resolveFirecrawlApiKeys({}, noEnv), [], "no key means the keyless tier");

// --- the pool as the adapters see it ---

assert.deepEqual(allFirecrawlKeys({ firecrawlApiKeys: ["a", " b ", ""] }), ["a", "b"]);
assert.deepEqual(allFirecrawlKeys({ firecrawlApiKey: "only" }), ["only"]);
assert.deepEqual(allFirecrawlKeys({}), []);
assert.equal(hasFirecrawlApiKey({ firecrawlApiKeys: ["a"] }), true);
assert.equal(hasFirecrawlApiKey({}), false);
assert.equal(firecrawlAuthMode({ firecrawlApiKeys: ["a"] }), "api_key");
assert.equal(firecrawlAuthMode({}), "keyless");

// --- quota classification ---

assert.equal(isFirecrawlQuotaError({ status: 402 }), true);
assert.equal(isFirecrawlQuotaError({ status: 429, upstreamCode: "credits" }), true);
assert.equal(isFirecrawlQuotaError({ status: 429 }), false, "a bare 429 is a rate limit, not a spent key");
assert.equal(isFirecrawlQuotaError({ status: 500 }), false);
assert.equal(isFirecrawlKeySpentError({ status: 402 }), true);
assert.equal(isFirecrawlKeySpentError({ status: 429, upstreamCode: "credits" }), true);
assert.equal(isFirecrawlKeySpentError({ status: 401 }), true, "an invalid key is skipped in favour of a sibling");
assert.equal(isFirecrawlKeySpentError({ status: 429 }), false, "a rate limit is transient");
assert.equal(isFirecrawlKeySpentError({ status: 500 }), false, "a server error is nobody's fault");
assert.equal(isFirecrawlKeySpentError({ status: 403 }), false);

// --- the fingerprint never carries key material ---

{
  const fingerprint = firecrawlKeyFingerprint("fc-secret-key-value");
  assert.equal(fingerprint.length, 16);
  assert.equal(fingerprint.includes("fc-secret"), false);
  assert.notEqual(fingerprint, firecrawlKeyFingerprint("fc-other-key"));
  assert.equal(fingerprint, firecrawlKeyFingerprint(" fc-secret-key-value "), "the fingerprint ignores surrounding space");
  assert.equal(firecrawlKeyFingerprint(""), "");
}

// --- round-robin: consecutive calls advance through the pool ---

const dir = mkdtempSync(path.join(tmpdir(), "grok-search-firecrawl-rr-"));
const rrPath = path.join(dir, "firecrawl-rr.json");
const poolConfig = {
  firecrawlApiKeys: ["k0", "k1", "k2"],
  firecrawlApiKey: "k0",
  firecrawlRoundRobinPath: rrPath,
  stateDir: dir,
};

assert.equal(loadFirecrawlRoundRobinIndex(3, poolConfig), 0);
assert.deepEqual(nextFirecrawlApiKey(poolConfig), { key: "k0", index: 0, total: 3 });
assert.equal(loadFirecrawlRoundRobinIndex(3, poolConfig), 1);
assert.deepEqual(nextFirecrawlApiKey(poolConfig), { key: "k1", index: 1, total: 3 });
assert.deepEqual(nextFirecrawlApiKey(poolConfig), { key: "k2", index: 2, total: 3 });
// The cursor wraps back to the first key.
assert.deepEqual(nextFirecrawlApiKey(poolConfig), { key: "k0", index: 0, total: 3 });

// The cursor survives across processes: it is read from and written to disk.
{
  const stored = JSON.parse(await readFile(rrPath, "utf8"));
  assert.equal(stored.nextIndex, 1);
  saveFirecrawlRoundRobinIndex(7, poolConfig);
  assert.equal(loadFirecrawlRoundRobinIndex(3, poolConfig), 1, "the index wraps into the key count");
}

// A corrupt cursor file degrades to the first key instead of throwing.
{
  const corruptPath = path.join(dir, "corrupt-rr.json");
  await writeFile(corruptPath, "not json", "utf8");
  assert.equal(loadFirecrawlRoundRobinIndex(3, { ...poolConfig, firecrawlRoundRobinPath: corruptPath }), 0);
}

// --- the pool rotates onto the next key when one is spent ---

const stateDir = await mkdtemp(path.join(tmpdir(), "grok-search-firecrawl-state-"));

async function withServer(handler, callback) {
  const server = createServer(handler);
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  try {
    return await callback(`http://127.0.0.1:${server.address().port}`);
  } finally {
    server.close();
  }
}

function readBody(req, callback) {
  let body = "";
  req.setEncoding("utf8");
  req.on("data", (chunk) => {
    body += chunk;
  });
  req.on("end", () => callback(body ? JSON.parse(body) : {}));
}

const creditsBody = JSON.stringify({
  success: false,
  error: "Insufficient credits",
  reason: "credits",
  retry_after_seconds: 3600,
});

{
  const seen = [];
  await withServer(
    (req, res) => {
      readBody(req, () => {});
      seen.push(req.headers.authorization);
      // The first key is spent; the second one works.
      if (seen.length === 1) {
        res.writeHead(429, { "content-type": "application/json" });
        res.end(creditsBody);
        return;
      }
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ success: true, data: { web: [{ url: "https://example.com/a" }] } }));
    },
    async (base) => {
      const result = await firecrawlSearch("query", 2, {
        ...poolConfig,
        stateDir,
        firecrawlApiUrl: base,
        firecrawlRoundRobinPath: path.join(dir, "rotate-rr.json"),
        retryMaxAttempts: 1,
      });
      assert.equal(result.ok, true, "the second key answers");
      assert.equal(result.sources.length, 1);
      assert.equal(result.firecrawl_key_index, 1, "the successful key is reported");
      assert.equal(result.firecrawl_key_total, 3);
      assert.equal(result.firecrawl_keys_tried, 2, "both keys were tried");
      assert.deepEqual(
        seen,
        ["Bearer k0", "Bearer k1"],
        "the pool falls through to the next key after the first is spent"
      );
    }
  );
}

// The spent key is in cooldown; the working one is not.
{
  const state = await readFirecrawlCooldownState({ stateDir });
  assert.ok(state.keys[firecrawlKeyFingerprint("k0")], "the spent key is cooling down");
  assert.equal(state.keys[firecrawlKeyFingerprint("k1")], undefined, "the working key is not");
  // One spent key does not switch the whole channel off.
  assert.equal(await firecrawlChannelCooldown({ ...poolConfig, stateDir }), null);
}

// A cooling key is skipped in favour of a sibling.
{
  const seen = [];
  await withServer(
    (req, res) => {
      readBody(req, () => {});
      seen.push(req.headers.authorization);
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ success: true, data: { web: [] } }));
    },
    async (base) => {
      const result = await firecrawlSearch("query", 2, {
        ...poolConfig,
        stateDir,
        firecrawlApiUrl: base,
        // A fresh cursor starts at k0, which is cooling, so the pool moves on to k1.
        firecrawlRoundRobinPath: path.join(dir, "skip-rr.json"),
        retryMaxAttempts: 1,
      });
      assert.equal(result.ok, true);
      assert.deepEqual(seen, ["Bearer k1"], "the cooling key is not asked again");
      assert.equal(result.firecrawl_key_index, 1);
    }
  );
}

// When every key is cooling, the channel is dead and later commands skip it.
{
  const config = { ...poolConfig, stateDir };
  // k0 is already cooling from the rotation test above; add the other two.
  await recordFirecrawlCooldown(config, {
    authMode: "api_key",
    fingerprint: firecrawlKeyFingerprint("k1"),
    retryAfterMs: 60_000,
  });
  await recordFirecrawlCooldown(config, {
    authMode: "api_key",
    fingerprint: firecrawlKeyFingerprint("k2"),
    retryAfterMs: 60_000,
  });
  assert.ok(await firecrawlChannelCooldown(config), "every key cooling means the channel is dead");
}

// A key that works again is taken out of cooldown.
{
  const recoverState = await mkdtemp(path.join(tmpdir(), "grok-search-firecrawl-recover-"));
  const config = {
    firecrawlApiKeys: ["k1"],
    firecrawlApiKey: "k1",
    stateDir: recoverState,
    firecrawlRoundRobinPath: path.join(dir, "recover-rr.json"),
    retryMaxAttempts: 1,
  };
  await recordFirecrawlCooldown(config, {
    authMode: "api_key",
    fingerprint: firecrawlKeyFingerprint("k1"),
    retryAfterMs: 60_000,
  });
  await withServer(
    (req, res) => {
      readBody(req, () => {});
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ success: true, data: { web: [] } }));
    },
    async (base) => {
      const result = await firecrawlSearch("query", 1, { ...config, firecrawlApiUrl: base });
      assert.equal(result.ok, true);
      const state = await readFirecrawlCooldownState(config);
      assert.equal(state.keys[firecrawlKeyFingerprint("k1")], undefined, "a successful key leaves the cooldown");
    }
  );
}

// The keyless tier still works and keeps its own cooldown slot.
{
  await withServer(
    (req, res) => {
      readBody(req, () => {});
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ success: true, data: { web: [{ url: "https://example.com/keyless" }] } }));
    },
    async (base) => {
      const result = await firecrawlSearch("query", 2, {
        stateDir,
        firecrawlApiUrl: base,
        retryMaxAttempts: 1,
      });
      assert.equal(result.ok, true);
      assert.equal(result.auth_mode, "keyless");
      assert.equal(result.firecrawl_key_index, -1, "the keyless tier has no key index");
      assert.equal(result.firecrawl_key_total, 0);
    }
  );
}

// A successful call must not carry an `error` field. The downstream failure summary filters
// on the presence of `error` rather than on `ok`, so a stray error field would make a
// successful provider look like the cause of someone else's failure.
{
  await withServer(
    (req, res) => {
      readBody(req, () => {});
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ success: true, data: { web: [{ url: "https://example.com/clean" }] } }));
    },
    async (base) => {
      const result = await firecrawlSearch("query", 2, {
        firecrawlApiKeys: ["k0"],
        firecrawlApiKey: "k0",
        stateDir,
        firecrawlApiUrl: base,
        firecrawlRoundRobinPath: path.join(dir, "clean-rr.json"),
        retryMaxAttempts: 1,
      });
      assert.equal(result.ok, true);
      assert.equal("error" in result, false, "a successful search carries no error field");
      assert.equal(result.sources.length, 1);
    }
  );
}

// A soft failure (upstream said success:false) proves nothing about the key's allowance, so
// it must not wipe a legitimate cooldown record for that key.
{
  const softState = await mkdtemp(path.join(tmpdir(), "grok-search-firecrawl-soft-"));
  const config = {
    firecrawlApiKeys: ["k0"],
    firecrawlApiKey: "k0",
    stateDir: softState,
    firecrawlRoundRobinPath: path.join(dir, "soft-rr.json"),
    retryMaxAttempts: 1,
  };
  await recordFirecrawlCooldown(config, {
    authMode: "api_key",
    fingerprint: firecrawlKeyFingerprint("k0"),
    retryAfterMs: 60_000,
  });
  await withServer(
    (req, res) => {
      readBody(req, () => {});
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ success: false, error: "target blocked" }));
    },
    async (base) => {
      const result = await firecrawlScrape("https://example.com/page", { ...config, firecrawlApiUrl: base });
      assert.equal(result.ok, false);
      const state = await readFirecrawlCooldownState(config);
      assert.ok(
        state.keys[firecrawlKeyFingerprint("k0")],
        "a soft failure keeps the key in cooldown"
      );
    }
  );
}

rmSync(dir, { recursive: true, force: true });

console.log("firecrawl-keys.test.js: ok");
