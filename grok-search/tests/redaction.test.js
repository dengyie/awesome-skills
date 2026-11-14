#!/usr/bin/env node
// Error bodies are truncated before they reach a message that lands in the run record. The
// truncation used to run first, so a secret straddling the cut survived as a fragment short
// enough to slip past redactSecrets' replacement: five characters of a live key, verbatim.
// Redact first, then truncate.
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { requestJson } from "../scripts/lib/http.js";

const secret = "sk-live-0123456789abcdefghij";
const config = { grokApiKey: secret, retryMaxAttempts: 1, debug: false };

const server = createServer((req, res) => {
  req.resume();
  // Place the key so the 500-character cut splits it: the old order left "sk-li" behind.
  const body = `${"x".repeat(495)}${secret}`;
  res.writeHead(500, { "content-type": "application/json" });
  res.end(body);
});
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));

let error = null;
try {
  await requestJson(`http://127.0.0.1:${server.address().port}/v1/responses`, {
    headers: { "content-type": "application/json" },
    body: { q: "x" },
    timeoutMs: 5_000,
    config,
    retry: false,
  });
} catch (caught) {
  error = caught;
}

assert.ok(error, "a 500 must throw");
assert.equal(error.status, 500);
assert.ok(!error.message.includes(secret.slice(0, 5)), `the truncated body must not leak a key prefix: ${error.message}`);
assert.ok(error.message.includes("***"), "the secret is masked, not dropped");
assert.ok(error.message.length <= 600, "the body is still bounded");

// A body whose only content is the key keeps the useful part of the message.
const direct = createServer((req, res) => {
  req.resume();
  res.writeHead(401, { "content-type": "application/json" });
  res.end(JSON.stringify({ error: `invalid key ${secret}` }));
});
await new Promise((resolve) => direct.listen(0, "127.0.0.1", resolve));
let authError = null;
try {
  await requestJson(`http://127.0.0.1:${direct.address().port}/v1/responses`, {
    headers: {},
    body: {},
    timeoutMs: 5_000,
    config,
    retry: false,
  });
} catch (caught) {
  authError = caught;
}
assert.ok(authError);
assert.ok(!authError.message.includes(secret), "the whole key is masked");
assert.match(authError.message, /HTTP 401/);

// A credential field this module never heard of is redacted too: the scan is by field name, so
// a key added to the config later cannot reach an error message in plaintext.
const futureSecret = "tvly-future-key-9876543210";
const future = createServer((req, res) => {
  req.resume();
  res.writeHead(401, { "content-type": "application/json" });
  res.end(JSON.stringify({ error: `invalid key ${futureSecret}` }));
});
await new Promise((resolve) => future.listen(0, "127.0.0.1", resolve));
let futureError = null;
try {
  await requestJson(`http://127.0.0.1:${future.address().port}/v1/responses`, {
    headers: {},
    body: {},
    timeoutMs: 5_000,
    config: { retryMaxAttempts: 1, debug: false, brandNewApiKey: futureSecret },
    retry: false,
  });
} catch (caught) {
  futureError = caught;
}
assert.ok(!futureError.message.includes(futureSecret), "a credential field added later is masked too");
assert.ok(futureError.message.includes("***"), "the new field is masked, not dropped");

// A key field with no "api" in the name (tavilyProxyKey, and whatever gets added next) is
// still a credential; matching only `*ApiKey` left it in plaintext.
let proxyKeyError = null;
try {
  await requestJson(`http://127.0.0.1:${future.address().port}/v1/responses`, {
    headers: {},
    body: {},
    timeoutMs: 5_000,
    config: { retryMaxAttempts: 1, debug: false, tavilyProxyKey: futureSecret },
    retry: false,
  });
} catch (caught) {
  proxyKeyError = caught;
}
assert.ok(!proxyKeyError.message.includes(futureSecret), "a *Key field without an api prefix is masked");

server.close();
direct.close();
future.close();
console.log("redaction.test.js: ok");
