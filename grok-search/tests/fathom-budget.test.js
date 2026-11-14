#!/usr/bin/env node
// The fathom channel retries engine plans in sequence, so two things must hold:
// 1. The timeout is a total budget for the whole call, not per plan — a per-plan timeout
//    multiplies into minutes and can outlast the command deadline, killing a search that
//    already had Grok's answer.
// 2. `list_engines` decides the plan: an engine whose breaker is open is skipped, and the
//    fan-out over every engine runs last, because it waits for the slowest engine in the list.
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { mkdtempSync } from "node:fs";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import path from "node:path";
import { fathomSearch, hasFathomApiKey } from "../scripts/lib/fathom.js";

const pkgVersion = createRequire(import.meta.url)("../package.json").version;

const handshake = (frame, result) =>
  JSON.stringify({ jsonrpc: "2.0", id: frame.id, result });

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

const json = (res, payload) => {
  res.writeHead(200, { "content-type": "application/json" });
  res.end(payload);
};

// --- 1. slow server: the whole call stays inside its budget ---------------------------------
const hangMs = 4_000;
const slowServer = await listen((frame, res) => {
  if (frame.method === "initialize") return json(res, handshake(frame, { protocolVersion: "2024-11-05", capabilities: {} }));
  // Everything else holds the connection open, then answers far too late.
  setTimeout(() => {
    if (res.writableEnded) return;
    json(res, handshake(frame, { content: [] }));
  }, hangMs);
});

const slowConfig = {
  fathomApiUrl: `http://127.0.0.1:${slowServer.address().port}/mcp`,
  fathomApiKey: "test-token",
  fathomTimeoutMs: 400,
  stateDir: mkdtempSync(path.join(tmpdir(), "grok-fathom-budget-")),
};
assert.equal(hasFathomApiKey(slowConfig), true);

const startedAt = Date.now();
const slow = await fathomSearch("anything", 5, slowConfig, {});
const elapsed = Date.now() - startedAt;

assert.equal(slow.ok, false);
assert.equal(slow.provider, "fathom");
assert.deepEqual(slow.sources, []);
assert.ok(elapsed < 2_000, `the whole call must stay inside its budget, took ${elapsed}ms`);
assert.match(slow.error, /预算|超时/);
slowServer.close();

// --- 2. healthy probe: open engines are skipped, the working engine answers -----------------
const calls = [];
const healthyServer = await listen((frame, res) => {
  if (frame.method === "initialize") {
    // The handshake must report the real package version, not a stale literal.
    assert.equal(frame.params?.clientInfo?.version, pkgVersion);
    return json(res, handshake(frame, { protocolVersion: "2024-11-05", capabilities: {} }));
  }
  const tool = frame.params?.name;
  const args = frame.params?.arguments || {};
  calls.push({ tool, engines: args.engines });
  if (tool === "list_engines") {
    return json(
      res,
      handshake(frame, {
        structuredContent: {
          engines: [
            { name: "bing", circuit_state: "closed", initialized: true },
            { name: "duckduckgo", circuit_state: "open", initialized: true },
          ],
        },
      })
    );
  }
  if (args.engines === "bing") {
    return json(
      res,
      handshake(frame, {
        content: [{ type: "text", text: JSON.stringify({ results: [{ title: "Bing hit", url: "https://example.com/hit", snippet: "snippet" }] }) }],
      })
    );
  }
  // Any other plan fails: the test must prove bing was asked first.
  return json(res, handshake(frame, { isError: true, content: [{ type: "text", text: "engine unavailable" }] }));
});

const healthyConfig = {
  ...slowConfig,
  fathomApiUrl: `http://127.0.0.1:${healthyServer.address().port}/mcp`,
  stateDir: mkdtempSync(path.join(tmpdir(), "grok-fathom-healthy-")),
};
const fastStartedAt = Date.now();
const fast = await fathomSearch("anything", 5, healthyConfig, {});
const fastElapsed = Date.now() - fastStartedAt;

assert.equal(fast.ok, true, fast.error);
assert.equal(fast.fathom_engines, "bing", "the healthy single engine is used, not the fan-out");
assert.equal(fast.sources.length, 1);
assert.equal(fast.sources[0].url, "https://example.com/hit");
assert.ok(fastElapsed < 2_000, `a healthy engine answers immediately, took ${fastElapsed}ms`);
assert.deepEqual(
  calls.map((call) => call.engines),
  [undefined, "bing"],
  "one probe, then the healthy engine — the open engine is never tried"
);
healthyServer.close();

// --- 3. only non-favourite engines are closed: the shortlist follows the server, not a literal -
// Live servers rotate engine health; at one point google was closed while bing, duckduckgo and
// brave were all open. A plan built only from the hardcoded favourites then had nothing to do and
// the channel reported a failure without sending a request.
const altCalls = [];
const altServer = await listen((frame, res) => {
  if (frame.method === "initialize") return json(res, handshake(frame, { protocolVersion: "2024-11-05", capabilities: {} }));
  const args = frame.params?.arguments || {};
  altCalls.push({ tool: frame.params?.name, engines: args.engines });
  if (frame.params?.name === "list_engines") {
    return json(
      res,
      handshake(frame, {
        structuredContent: {
          engines: [
            { name: "google", circuit_state: "closed", initialized: true },
            { name: "bing", circuit_state: "open", initialized: true },
            { name: "duckduckgo", circuit_state: "open", initialized: true },
            { name: "brave", circuit_state: "open", initialized: true },
          ],
        },
      })
    );
  }
  if (args.engines === "google") {
    return json(
      res,
      handshake(frame, {
        content: [{ type: "text", text: JSON.stringify({ results: [{ title: "Google hit", url: "https://example.com/google" }] }) }],
      })
    );
  }
  return json(res, handshake(frame, { isError: true, content: [{ type: "text", text: "engine unavailable" }] }));
});

const alt = await fathomSearch("anything", 5, {
  ...healthyConfig,
  fathomApiUrl: `http://127.0.0.1:${altServer.address().port}/mcp`,
  stateDir: mkdtempSync(path.join(tmpdir(), "grok-fathom-alt-")),
}, {});
assert.equal(alt.ok, true, alt.error);
assert.equal(alt.fathom_engines, "google", "the closed engine from the server is used");
assert.deepEqual(altCalls.map((call) => call.engines), [undefined, "google"]);
altServer.close();

// --- 4. every breaker open: one bounded default call, and the error names the open engines -----
const deadCalls = [];
const deadServer = await listen((frame, res) => {
  if (frame.method === "initialize") return json(res, handshake(frame, { protocolVersion: "2024-11-05", capabilities: {} }));
  const args = frame.params?.arguments || {};
  deadCalls.push({ tool: frame.params?.name, engines: args.engines });
  if (frame.params?.name === "list_engines") {
    return json(
      res,
      handshake(frame, {
        structuredContent: {
          engines: [
            // A closed catalog engine is not a fallback: the mega tools reject it outright.
            { name: "arxiv", circuit_state: "closed" },
            { name: "bing", circuit_state: "open" },
            { name: "duckduckgo", circuit_state: "open" },
          ],
        },
      })
    );
  }
  return json(res, handshake(frame, { isError: true, content: [{ type: "text", text: "all_engines_failed" }] }));
});

const dead = await fathomSearch("anything", 5, {
  ...healthyConfig,
  fathomApiUrl: `http://127.0.0.1:${deadServer.address().port}/mcp`,
  stateDir: mkdtempSync(path.join(tmpdir(), "grok-fathom-dead-")),
}, {});
assert.equal(dead.ok, false);
assert.match(dead.error, /all_engines_failed/);
assert.match(dead.error, /open 引擎.*bing/);
assert.equal(deadCalls.length, 2, "probe plus one default call, not zero");
assert.equal(deadCalls[1].engines, undefined, "the fallback call lets the server route");
deadServer.close();

console.log("fathom-budget.test.js: ok");
// The slow stub's pending timers would keep the process alive for hangMs; nothing else is running.
process.exit(0);
