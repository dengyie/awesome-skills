#!/usr/bin/env node
// The live server rotates engine health, so the plan list is the whole reliability story:
// 1. Only engines whose breaker is `closed` may be planned. Measured on the live relay, an
//    `open` engine fails at once with `circuit_open` and a `half-open` one was still timing out
//    at the budget a closed engine answers in.
// 2. `mega_search` refuses a single-catalog engine, so a configured `arxiv` must never enter a
//    mega plan — one such name fails the whole call before any web engine runs.
// 3. A 502 `all_engines_failed` is the server's own engines failing, not relay death. It gets a
//    short cooldown, a relay error gets the full one, and any success clears both.
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { mkdtempSync } from "node:fs";
import { readFile, unlink, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { activeChannelCooldown, clearChannelCooldown, recordChannelCooldown } from "../scripts/lib/cooldown.js";
import { enginePlans, fathomSearch } from "../scripts/lib/fathom.js";

const buildArgs = (list) => (list ? { engines: list } : {});
const names = (plans) => plans.map((plan) => plan.args.engines);

// --- 1. plan selection is a pure function of the server's engine table -----------------------
// The live table: only yandex is closed, baidu and duckduckgo are half-open, the rest are open.
const liveProbe = {
  closed: ["yandex"],
  open: ["google", "bing", "duckduckgo", "brave", "ecosia", "grok", "baidu"],
};
assert.deepEqual(
  names(enginePlans({ probe: liveProbe, buildArgs })),
  ["yandex"],
  "one closed engine means one single-engine plan: half-open and open engines are not alternatives"
);

// Two closed engines: both single plans, then the fan-out — which waits for the slowest engine.
assert.deepEqual(
  names(enginePlans({ probe: { closed: ["bing", "duckduckgo"], open: ["google"] }, buildArgs })),
  ["bing", "duckduckgo", "bing,duckduckgo"],
  "the fan-out runs last and only over the closed engines"
);

// A closed catalog engine is not a plan: mega_search rejects it, so the channel falls back to
// the server's default routing instead of spending a call on a guaranteed refusal.
assert.deepEqual(
  names(enginePlans({ probe: { closed: ["arxiv"], open: [] }, buildArgs })),
  [],
  "a catalog engine is never planned; fathomSearch then asks the server to route"
);

// Configured engines lead, but the mega tool drops the ones it cannot accept.
assert.deepEqual(
  names(enginePlans({ engines: ["arxiv", "bing"], probe: null, buildArgs })).slice(0, 2),
  ["bing", "bing"],
  "the mega fan-out and the first single plan both skip the catalog engine"
);
assert.ok(
  !names(enginePlans({ engines: ["arxiv", "bing"], probe: null, buildArgs })).includes("arxiv"),
  "a configured catalog engine never reaches mega_search"
);
// A single-engine tool has no such rule, so the configured name survives.
assert.equal(
  names(enginePlans({ engines: ["arxiv"], probe: null, tool: "search", buildArgs }))[0],
  "arxiv",
  "the single-engine tool may still ask for a catalog engine"
);

// --- 2. engine-level failure gets a short cooldown, relay failure the full one --------------
const handshake = (frame, result) => JSON.stringify({ jsonrpc: "2.0", id: frame.id, result });
const json = (res, payload, status = 200) => {
  res.writeHead(status, { "content-type": "application/json" });
  res.end(payload);
};
function listen(handler) {
  const server = createServer((req, res) => {
    let raw = "";
    req.on("data", (chunk) => {
      raw += chunk;
    });
    req.on("end", () => handler(JSON.parse(raw || "{}"), res));
  });
  return new Promise((resolve) => server.listen(0, "127.0.0.1", () => resolve(server)));
}
const enginesTable = (engines) => ({ structuredContent: { engines } });

async function cooldownRecord(stateDir) {
  try {
    return JSON.parse(await readFile(path.join(stateDir, "fathom-cooldown.json"), "utf8"));
  } catch (error) {
    if (error.code === "ENOENT") return null;
    throw error;
  }
}
const minutes = (record) => Math.round((Date.parse(record.until) - Date.parse(record.hit_at)) / 60000);

// 2a. all_engines_failed: the relay answered, so the channel is not dead.
const engineFailServer = await listen((frame, res) => {
  if (frame.method === "initialize") return json(res, handshake(frame, { protocolVersion: "2024-11-05", capabilities: {} }));
  if (frame.params?.name === "list_engines") {
    return json(res, handshake(frame, enginesTable([{ name: "yandex", circuit_state: "closed" }, { name: "google", circuit_state: "open" }])));
  }
  return json(
    res,
    handshake(frame, {
      isError: true,
      content: [
        {
          type: "text",
          text: 'HTTP 502: {"error":"all_engines_failed","meta":{"engine":"mega","engine_errors":[{"engine":"yandex","error":"request_timeout"}]}}',
        },
      ],
    })
  );
});
const engineFailConfig = {
  fathomApiUrl: `http://127.0.0.1:${engineFailServer.address().port}/mcp`,
  fathomApiKey: "test-token",
  stateDir: mkdtempSync(path.join(tmpdir(), "grok-fathom-enginefail-")),
};
const engineFail = await fathomSearch("anything", 3, engineFailConfig, {});
assert.equal(engineFail.ok, false);
assert.match(engineFail.error, /all_engines_failed/);
const shortRecord = await cooldownRecord(engineFailConfig.stateDir);
assert.ok(shortRecord, "a total engine failure still records a cooldown");
assert.equal(shortRecord.reason, "all_engines_failed");
assert.ok(minutes(shortRecord) <= 5, `an engine failure must not disable the channel for the full window, got ${minutes(shortRecord)}m`);
engineFailServer.close();

// 2b. a plain 500 is the relay itself failing: the full cooldown applies.
const relayFailServer = await listen((frame, res) => {
  if (frame.method === "initialize") return json(res, handshake(frame, { protocolVersion: "2024-11-05", capabilities: {} }));
  if (frame.params?.name === "list_engines") {
    return json(res, handshake(frame, { isError: true, content: [{ type: "text", text: "probe down" }] }));
  }
  return json(res, "upstream unavailable", 500);
});
const relayFailConfig = {
  fathomApiUrl: `http://127.0.0.1:${relayFailServer.address().port}/mcp`,
  fathomApiKey: "test-token",
  stateDir: mkdtempSync(path.join(tmpdir(), "grok-fathom-relayfail-")),
};
const relayFail = await fathomSearch("anything", 3, relayFailConfig, {});
assert.equal(relayFail.ok, false);
const fullRecord = await cooldownRecord(relayFailConfig.stateDir);
assert.ok(fullRecord, "a relay 500 opens a cooldown");
assert.equal(fullRecord.reason, "http_500");
assert.ok(minutes(fullRecord) >= 10, `a relay failure keeps the full window, got ${minutes(fullRecord)}m`);
relayFailServer.close();

// --- 3. a success clears the cooldown it outlived ------------------------------------------
const okServer = await listen((frame, res) => {
  if (frame.method === "initialize") return json(res, handshake(frame, { protocolVersion: "2024-11-05", capabilities: {} }));
  if (frame.params?.name === "list_engines") {
    return json(res, handshake(frame, enginesTable([{ name: "bing", circuit_state: "closed" }])));
  }
  return json(
    res,
    handshake(frame, {
      content: [{ type: "text", text: JSON.stringify({ results: [{ title: "hit", url: "https://example.com/hit" }] }) }],
    })
  );
});
const okConfig = {
  fathomApiUrl: `http://127.0.0.1:${okServer.address().port}/mcp`,
  fathomApiKey: "test-token",
  stateDir: mkdtempSync(path.join(tmpdir(), "grok-fathom-clear-")),
};
await recordChannelCooldown(okConfig, "fathom", { authMode: okConfig.fathomApiUrl, reason: "http_502" });
assert.ok(await cooldownRecord(okConfig.stateDir), "precondition: the cooldown exists");
const recovered = await fathomSearch("anything", 3, okConfig, {});
assert.equal(recovered.ok, true, recovered.error);
assert.equal(await cooldownRecord(okConfig.stateDir), null, "a working search clears the cooldown");
okServer.close();

// --- 4. the cooldown gate matches the endpoint, not the raw config string -------------------
// search-extras passes `config.fathomApiUrl` while the record stores the trimmed URL; a trailing
// space used to make the cooldown silently ineffective.
const padConfig = { ...okConfig, stateDir: mkdtempSync(path.join(tmpdir(), "grok-fathom-gate-")) };
const written = await recordChannelCooldown(padConfig, "fathom", { authMode: padConfig.fathomApiUrl, reason: "http_500" });
assert.ok(written);
assert.ok(
  await activeChannelCooldown(padConfig, "fathom", `  ${padConfig.fathomApiUrl}  `),
  "a padded config URL still matches the record"
);
assert.equal(await activeChannelCooldown(padConfig, "fathom", "http://elsewhere/mcp"), null, "another endpoint is unaffected");
// Clearing is scoped the same way: a success on another endpoint must not hide a broken URL.
await clearChannelCooldown(padConfig, "fathom", "http://elsewhere/mcp");
assert.ok(await cooldownRecord(padConfig.stateDir), "another endpoint's success leaves the record alone");
await unlink(path.join(padConfig.stateDir, "fathom-cooldown.json")).catch(() => {});

// --- 5. a failed probe falls back to its own last table, not to the eight-engine ladder ------
// The live relay failed `list_engines` while a 136-second-old cache still said yandex was the only
// closed engine. Without the fallback the call walked the whole ladder and spent 28.5s of its 30s
// budget; the cached single engine answered in 4.9s.
const staleCalls = [];
const staleServer = await listen((frame, res) => {
  if (frame.method === "initialize") return json(res, handshake(frame, { protocolVersion: "2024-11-05", capabilities: {} }));
  const args = frame.params?.arguments || {};
  staleCalls.push({ tool: frame.params?.name, engines: args.engines });
  if (frame.params?.name === "list_engines") {
    return json(res, handshake(frame, { isError: true, content: [{ type: "text", text: "probe down" }] }));
  }
  if (args.engines === "bing") {
    return json(
      res,
      handshake(frame, {
        content: [{ type: "text", text: JSON.stringify({ results: [{ title: "Stale hit", url: "https://example.com/stale" }] }) }],
      })
    );
  }
  return json(res, handshake(frame, { isError: true, content: [{ type: "text", text: "engine unavailable" }] }));
});
const staleConfig = {
  fathomApiUrl: `http://127.0.0.1:${staleServer.address().port}/mcp`,
  fathomApiKey: "test-token",
  stateDir: mkdtempSync(path.join(tmpdir(), "grok-fathom-stale-")),
};
await writeFile(
  path.join(staleConfig.stateDir, "fathom-engines.json"),
  JSON.stringify({
    auth_mode: staleConfig.fathomApiUrl,
    at: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
    engines: [{ name: "bing", circuit_state: "closed" }, { name: "google", circuit_state: "open" }],
  })
);
const stale = await fathomSearch("anything", 3, staleConfig, {});
assert.equal(stale.ok, true, stale.error);
assert.equal(stale.fathom_engines, "bing", "the last known table decides the plan");
assert.deepEqual(
  staleCalls.map((call) => call.engines),
  [undefined, "bing"],
  "one failed probe, then the cached engine — the ladder is never walked"
);
staleServer.close();

console.log("fathom-plans.test.js: ok");
process.exit(0);
