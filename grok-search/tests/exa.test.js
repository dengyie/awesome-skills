#!/usr/bin/env node
import assert from "node:assert/strict";
import { mkdtemp } from "node:fs/promises";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import path from "node:path";
import { activeExaCooldown, clearExaCooldown } from "../scripts/lib/cooldown.js";
import { exaExtract, exaSearch, extraAllocation, hasExaApiKey } from "../scripts/lib/providers.js";
import { classifyGrokFailure } from "../scripts/lib/grok-responses.js";

const stateDir = await mkdtemp(path.join(tmpdir(), "grok-search-state-"));
const baseConfig = {
  retryMaxAttempts: 3,
  retryMultiplier: 0,
  retryMaxWait: 0.05,
  debug: false,
  exaApiKey: "test-exa-key",
  exaApiUrl: "",
  tavilyApiKeys: [],
  tavilyApiKey: "",
  stateDir,
};

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

const searchResponse = {
  requestId: "req-1",
  results: [
    {
      title: "Node.js Releases",
      url: "https://nodejs.org/en/about/previous-releases",
      publishedDate: "2026-10-27T00:00:00.000Z",
      highlights: ["Node.js 26 Lithium is the current Active LTS."],
      highlightScores: [0.42],
    },
    { url: "", title: "dropped: no url" },
    { url: "https://example.com/no-title-url", highlights: [] },
  ],
  costDollars: { total: 0.007 },
};

// Search: body vocabulary (query/type/numResults/contents.highlights + domain filters reach
// the request as includeDomains/excludeDomains), and row mapping into source cards.
await withServer(
  (req, res) => {
    readBody(req, (body) => {
      req.__body = body;
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify(searchResponse));
    });
  },
  async (base) => {
    const config = { ...baseConfig, exaApiUrl: base };
    const result = await exaSearch("node lts version", 2, config, {
      allowedDomains: ["github.com"],
      excludedDomains: ["medium.com"],
    });
    assert.equal(result.ok, true);
    assert.equal(result.provider, "exa");
    assert.deepEqual(result.sources[0], {
      url: "https://nodejs.org/en/about/previous-releases",
      provider: "exa",
      title: "Node.js Releases",
      description: "Node.js 26 Lithium is the current Active LTS.",
      published_date: "2026-10-27T00:00:00.000Z",
      score: 0.42,
    });
    // Rows without a URL are dropped; a title-less row still survives with just the URL.
    assert.equal(result.sources.length, 2);
    assert.deepEqual(result.sources[1], { url: "https://example.com/no-title-url", provider: "exa" });
    assert.equal(result.cost_usd, 0.007);
    assert.equal(result.requests, 1);
  }
);

await withServer(
  (req, res) => {
    readBody(req, (body) => {
      assert.equal(body.query, "node lts version");
      assert.equal(body.type, "auto");
      assert.equal(body.numResults, 2);
      assert.deepEqual(body.contents, { highlights: true });
      assert.deepEqual(body.includeDomains, ["github.com"]);
      assert.deepEqual(body.excludeDomains, ["medium.com"]);
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ results: [] }));
    });
  },
  async (base) => {
    await exaSearch("node lts version", 2, { ...baseConfig, exaApiUrl: base }, {
      allowedDomains: ["github.com"],
      excludedDomains: ["medium.com"],
    });
  }
);

// numResults is clamped to Exa's documented maximum of 100 so a huge --extra
// degrades gracefully instead of failing the channel with INVALID_REQUEST_BODY.
await withServer(
  (req, res) => {
    readBody(req, (body) => {
      assert.equal(body.numResults, 100);
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ results: [] }));
    });
  },
  async (base) => {
    const result = await exaSearch("q", 500, { ...baseConfig, exaApiUrl: base });
    assert.equal(result.ok, true);
  }
);

// No filters: the arrays stay out of the body entirely.
await withServer(
  (req, res) => {
    readBody(req, (body) => {
      assert.equal("includeDomains" in body, false);
      assert.equal("excludeDomains" in body, false);
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ results: [] }));
    });
  },
  async (base) => {
    await exaSearch("node lts version", 2, { ...baseConfig, exaApiUrl: base });
  }
);

// Missing key: a skip, not an error.
{
  const result = await exaSearch("q", 2, { ...baseConfig, exaApiKey: "" });
  assert.deepEqual(result, { ok: false, provider: "exa", skipped: true, error: "EXA_API_KEY 未配置", sources: [] });
  assert.equal(hasExaApiKey({ ...baseConfig, exaApiKey: "" }), false);
}

// Balance exhausted (402): quota flag plus a cooldown record the next run can skip.
await withServer(
  (req, res) => {
    req.resume();
    res.writeHead(402, { "content-type": "application/json" });
    res.end(JSON.stringify({ requestId: "r", error: "Payment Required", tag: "PAYMENT_REQUIRED" }));
  },
  async (base) => {
    await clearExaCooldown(baseConfig);
    const result = await exaSearch("q", 2, { ...baseConfig, exaApiUrl: base });
    assert.equal(result.ok, false);
    assert.equal(result.quota_exhausted, true);
    const cooldown = await activeExaCooldown(baseConfig);
    assert.ok(cooldown, "cooldown recorded");
    await clearExaCooldown(baseConfig);
  }
);

// Extract: /contents body, success mapping, status failure and empty text.
await withServer(
  (req, res) => {
    readBody(req, (body) => {
      req.__body = body;
      res.writeHead(200, { "content-type": "application/json" });
      res.end(
        JSON.stringify({
          requestId: "req-2",
          results: [{ url: "https://example.com/a", title: "Example", publishedDate: "2026-01-02T00:00:00.000Z", text: "# Hello\n\nBody text." }],
          statuses: [{ id: "https://example.com/a", status: "success", source: "cached" }],
          costDollars: { total: 0.001 },
        })
      );
    });
  },
  async (base) => {
    const config = { ...baseConfig, exaApiUrl: base };
    const result = await exaExtract("https://example.com/a", config, { maxChars: 4000 });
    assert.equal(result.ok, true);
    assert.equal(result.provider, "exa");
    assert.equal(result.content, "# Hello\n\nBody text.");
    assert.deepEqual(result.metadata, {
      source_url: "https://example.com/a",
      title: "Example",
      published_at: "2026-01-02T00:00:00.000Z",
    });
    assert.equal(result.cost_usd, 0.001);
  }
);

await withServer(
  (req, res) => {
    readBody(req, (body) => {
      assert.deepEqual(body.urls, ["https://example.com/a"]);
      assert.deepEqual(body.text, { maxCharacters: 4000 });
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ results: [], statuses: [{ id: "https://example.com/a", status: "failed" }] }));
    });
  },
  async (base) => {
    const result = await exaExtract("https://example.com/a", { ...baseConfig, exaApiUrl: base }, { maxChars: 4000 });
    assert.equal(result.ok, false);
    assert.match(result.error, /failed/);
  }
);

// extraAllocation: every configured channel searches the full target; the union is deduped
// downstream. A missing key or cooldown drops that channel entirely.
{
  const withExa = { ...baseConfig, tavilyApiKeys: ["tvly-x"] };
  assert.deepEqual(extraAllocation(6, withExa), { tavily: 6, firecrawl: 6, exa: 6 });
  assert.deepEqual(extraAllocation(1, withExa), { tavily: 1, firecrawl: 1, exa: 1 });
  assert.deepEqual(extraAllocation(6, withExa, { exaAvailable: false }), { tavily: 6, firecrawl: 6, exa: 0 });
  // No Tavily key: Firecrawl and Exa each take the full target.
  assert.deepEqual(extraAllocation(6, baseConfig), { tavily: 0, firecrawl: 6, exa: 6 });
  assert.deepEqual(extraAllocation(6, baseConfig, { exaAvailable: false }), { tavily: 0, firecrawl: 6, exa: 0 });
  // Firecrawl cooling down: the remaining channels still search the full target.
  assert.deepEqual(extraAllocation(4, withExa, { firecrawlAvailable: false }), { tavily: 4, firecrawl: 0, exa: 4 });
  assert.deepEqual(extraAllocation(0, withExa), { tavily: 0, firecrawl: 0, exa: 0 });
}

// classifyGrokFailure: the wxiai relay answers an empty balance with 403 +
// insufficient_user_usd_credit, which must classify as quota so the degraded
// Tavily/Firecrawl/Exa fallback can take over.
{
  const wxiai = {
    status: 403,
    message: 'HTTP 403: {"error":{"message":"预扣费失败，用户美元信用积分: ＄0.007186，所需金额: ＄0.024277","code":"insufficient_user_usd_credit"}}',
  };
  assert.equal(classifyGrokFailure(wxiai), "quota");
  // The code alone is enough even without a Chinese message body.
  assert.equal(classifyGrokFailure({ status: 403, code: "insufficient_user_usd_credit", message: "HTTP 403" }), "quota");
  assert.equal(classifyGrokFailure({ status: 402, message: "payment required" }), "quota");
  assert.equal(classifyGrokFailure({ status: 429, message: "too many requests" }), "rate_limit");
  assert.equal(classifyGrokFailure({ status: 429, message: "quota exceeded" }), "quota");
  assert.equal(classifyGrokFailure({ status: 500, message: "internal error" }), null);
  assert.equal(classifyGrokFailure({ status: 403, message: "forbidden region" }), null);
}

console.log("exa.test.js: ok");
