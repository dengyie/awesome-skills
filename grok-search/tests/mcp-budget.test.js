#!/usr/bin/env node
// One MCP search is two round trips (initialize, then tools/call). They are one caller-visible
// wait, so they must share one timeout: a server that answers the handshake slowly and then
// stalls used to spend the handshake's time *and* the full budget on the tool call, doubling
// the wait past what the caller asked for (fathom's total budget is 30s).
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { mcpSearch } from "../scripts/lib/mcp.js";

const handshakeDelayMs = 300;
let toolCalls = 0;
let handshakes = 0;

const server = createServer((req, res) => {
  let raw = "";
  req.on("data", (chunk) => {
    raw += chunk;
  });
  req.on("end", () => {
    const frame = JSON.parse(raw || "{}");
    if (frame.method === "initialize") {
      handshakes += 1;
      setTimeout(() => {
        res.writeHead(200, { "content-type": "application/json" });
        res.end(JSON.stringify({ jsonrpc: "2.0", id: frame.id, result: { protocolVersion: "2024-11-05", capabilities: {} } }));
      }, handshakeDelayMs);
      return;
    }
    // The tool call never answers: the caller's budget has to end the wait.
    toolCalls += 1;
  });
});
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const url = `http://127.0.0.1:${server.address().port}/mcp`;

const budgetMs = 400;
const startedAt = Date.now();
let error = null;
try {
  await mcpSearch(url, "test-token", "search", { text: "q" }, { timeoutMs: budgetMs, config: {} });
} catch (caught) {
  error = caught;
}
const elapsed = Date.now() - startedAt;

assert.ok(error, "a stalled tool call must fail rather than hang");
assert.equal(error.timedOut, true, "the failure is a timeout, so fathom can report its budget");
assert.equal(handshakes, 1);
assert.equal(toolCalls, 1, "the tool call is still sent: only its wait is shortened");
assert.ok(
  elapsed < budgetMs + 250,
  `the handshake and the tool call share one budget; took ${elapsed}ms for a ${budgetMs}ms budget`
);
assert.ok(elapsed >= handshakeDelayMs, "the handshake delay is part of the measured wait");

server.close();

// A tool that fails inside an HTTP 200 answer reports the cause in its text, and the caller
// needs the status from it: fathom must tell a dead relay (401/403) from its own upstream
// engines failing (502 `all_engines_failed`) to choose the cooldown. The isError path used to
// drop the status, so every tool-level failure looked unexplained.
const toolErrorServer = createServer((req, res) => {
  let raw = "";
  req.on("data", (chunk) => {
    raw += chunk;
  });
  req.on("end", () => {
    const frame = JSON.parse(raw || "{}");
    const result =
      frame.method === "initialize"
        ? { protocolVersion: "2024-11-05", capabilities: {} }
        : { isError: true, content: [{ type: "text", text: 'HTTP 502: {"error":"all_engines_failed"}' }] };
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify({ jsonrpc: "2.0", id: frame.id, result }));
  });
});
await new Promise((resolve) => toolErrorServer.listen(0, "127.0.0.1", resolve));

let toolError = null;
try {
  await mcpSearch(`http://127.0.0.1:${toolErrorServer.address().port}/mcp`, "test-token", "search", { text: "q" }, { timeoutMs: 2_000, config: {} });
} catch (caught) {
  toolError = caught;
}
assert.ok(toolError, "an isError answer must fail the call");
assert.equal(toolError.status, 502, "the status is recovered from the tool's own error text");
assert.match(toolError.message, /all_engines_failed/);
toolErrorServer.close();

console.log("mcp-budget.test.js: ok");
process.exit(0);
