#!/usr/bin/env node
// Fallback contract for the Grok upstream:
// 1. A NO_SEARCH reply is a real, billed completion. Its text must survive on the error so
//    search.js can hand it back (marked ungrounded) instead of discarding a paid answer.
// 2. A transient 5xx or timeout opens a short cooldown, not the 15-minute default: one relay
//    blip must not turn into fifteen minutes of degraded answers.
// 3. A durable quota failure (402) still gets the long cooldown.
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { existsSync, mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { GROK_TRANSIENT_COOLDOWN_MS, searchGrokResponses } from "../scripts/lib/grok-responses.js";
import { ungroundedAnswer } from "../scripts/lib/search-degrade.js";

function listen(handler) {
  const server = createServer(handler);
  return new Promise((resolve) => server.listen(0, "127.0.0.1", () => resolve(server)));
}

function baseConfig(server, stateDir) {
  return {
    apiProvider: "openai-compatible",
    grokApiUrl: `http://127.0.0.1:${server.address().port}/v1`,
    grokApiKey: "test-key",
    stateDir,
    retryMaxAttempts: 1,
    retryMaxWait: 0,
    retryMultiplier: 0,
  };
}

// search.js always passes the resolved domain/handle filters; the body builder reads them.
const options = {
  model: "grok-4.7",
  searchSource: "web",
  maxTurns: 1,
  allowedDomains: [],
  excludedDomains: [],
  allowedXHandles: [],
  excludedXHandles: [],
};

// --- 1. text-only reply: NO_SEARCH keeps the paid answer ---------------------------------
const textOnly = {
  model: "grok-4.7",
  output: [{ type: "message", content: [{ type: "output_text", text: "It is 02:00 UTC." }] }],
};
const noSearchServer = await listen((_req, res) => {
  res.writeHead(200, { "content-type": "application/json" });
  res.end(JSON.stringify(textOnly));
});
try {
  const stateDir = mkdtempSync(path.join(tmpdir(), "grok-fallback-nosearch-"));
  await assert.rejects(
    () => searchGrokResponses("what time is it", options, baseConfig(noSearchServer, stateDir)),
    (error) => {
      assert.equal(error.code, "GROK_RESPONSES_NO_SEARCH");
      assert.equal(error.answer, "It is 02:00 UTC.", "the paid answer must survive on the error");
      assert.deepEqual(error.sources, []);
      assert.equal(error.diagnostics.responses_native_search, false);
      return true;
    }
  );
} finally {
  noSearchServer.close();
}

// --- 2. transient 5xx: short cooldown ----------------------------------------------------
const failingServer = await listen((_req, res) => {
  res.writeHead(500, { "content-type": "application/json" });
  res.end(JSON.stringify({ error: { message: "upstream exploded" } }));
});
try {
  const stateDir = mkdtempSync(path.join(tmpdir(), "grok-fallback-transient-"));
  const startedAt = Date.now();
  await assert.rejects(
    () => searchGrokResponses("anything", options, baseConfig(failingServer, stateDir)),
    /HTTP 500/
  );
  const file = path.join(stateDir, "grok-cooldown.json");
  assert.ok(existsSync(file), "a 5xx must record a cooldown");
  const record = JSON.parse(readFileSync(file, "utf8"));
  const ttl = Date.parse(record.until) - startedAt;
  assert.ok(ttl > 0, `ttl must be in the future, got ${ttl}`);
  assert.ok(
    ttl <= GROK_TRANSIENT_COOLDOWN_MS + 5_000,
    `a transient failure must not hold the upstream for the 15-minute default, got ${ttl}ms`
  );
  assert.equal(record.reason, "http_500");
} finally {
  failingServer.close();
}

// --- 3. durable quota failure: long cooldown ---------------------------------------------
const quotaServer = await listen((_req, res) => {
  res.writeHead(402, { "content-type": "application/json" });
  res.end(JSON.stringify({ error: { message: "insufficient credits", code: "insufficient_user_usd_credit" } }));
});
try {
  const stateDir = mkdtempSync(path.join(tmpdir(), "grok-fallback-quota-"));
  const startedAt = Date.now();
  await assert.rejects(
    () => searchGrokResponses("anything", options, baseConfig(quotaServer, stateDir)),
    /HTTP 402/
  );
  const record = JSON.parse(readFileSync(path.join(stateDir, "grok-cooldown.json"), "utf8"));
  const ttl = Date.parse(record.until) - startedAt;
  assert.ok(ttl > 10 * 60 * 1000, `quota exhaustion must keep the long cooldown, got ${ttl}ms`);
} finally {
  quotaServer.close();
}

// --- 4. the ungrounded wrapper is loud ---------------------------------------------------
const wrapped = ungroundedAnswer("  Grok 4.7 shipped on 21 Sep 2026.  ");
assert.match(wrapped, /^> /);
assert.match(wrapped, /web_search/);
assert.ok(wrapped.endsWith("Grok 4.7 shipped on 21 Sep 2026."), "the text is kept verbatim and trimmed");

// --- 5. a truncated completion comes back, but flagged -----------------------------------
const truncatedServer = await listen((_req, res) => {
  res.writeHead(200, { "content-type": "application/json" });
  res.end(
    JSON.stringify({
      status: "incomplete",
      incomplete_details: { reason: "max_output_tokens" },
      model: options.model,
      output: [
        { type: "web_search_call", status: "completed", action: { type: "search", query: "q" } },
        { type: "message", content: [{ type: "output_text", text: "Partial answer" }] },
      ],
    })
  );
});
try {
  const stateDir = mkdtempSync(path.join(tmpdir(), "grok-fallback-truncated-"));
  const result = await searchGrokResponses("q", options, baseConfig(truncatedServer, stateDir));
  assert.equal(result.content, "Partial answer", "a cut-off completion is still returned");
  assert.equal(result.diagnostics.responses_status, "incomplete");
  assert.equal(result.diagnostics.responses_incomplete_reason, "max_output_tokens");
  assert.ok(
    result.diagnostics.warnings.some((warning) => warning.includes("max_output_tokens")),
    "the truncation must be visible to the caller"
  );
} finally {
  truncatedServer.close();
}

console.log("grok-fallback.test.js: ok");
