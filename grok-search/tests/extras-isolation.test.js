#!/usr/bin/env node
// The extras run in the same Promise.all as the Grok request. A channel that throws — a
// malformed payload, an fs error on its state file — used to reject the whole call and discard
// an answer Grok had already produced and billed. A throwing channel is now shaped like a
// failed channel, so the run reports it and still returns the Grok answer.
import assert from "node:assert/strict";
import { settleChannel } from "../scripts/lib/search-extras.js";

// A throwing channel becomes a failed channel with its provider name.
const failed = await settleChannel("exa", Promise.reject(new Error("unexpected end of JSON input")));
assert.deepEqual(failed, {
  provider: "exa",
  ok: false,
  sources: [],
  error: "unexpected end of JSON input",
});

// A non-Error throw still produces a message rather than "undefined".
const thrown = await settleChannel("fathom", Promise.reject("boom"));
assert.equal(thrown.ok, false);
assert.equal(thrown.error, "boom");

// A working channel passes through untouched, including its sources and metadata.
const okResult = { provider: "tavily", ok: true, sources: [{ url: "https://example.com/", provider: "tavily" }], credits_used: 1 };
assert.equal(await settleChannel("tavily", Promise.resolve(okResult)), okResult);

// A channel's own soft failure is not rewritten either.
const soft = { provider: "firecrawl", ok: false, sources: [], error: "Firecrawl Search 返回 success:false" };
assert.equal(await settleChannel("firecrawl", Promise.resolve(soft)), soft);

console.log("extras-isolation.test.js: ok");
