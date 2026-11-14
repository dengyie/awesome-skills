#!/usr/bin/env node
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { requestJson } from "../scripts/lib/providers.js";

const config = { retryMaxAttempts: 3, retryMultiplier: 0, retryMaxWait: 0.05, debug: false };

async function withServer(handler, callback) {
  const server = createServer(handler);
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  try {
    return await callback(server.address().port);
  } finally {
    server.close();
  }
}

let requests = 0;

// A stable but malformed JSON response must not be retried.
await withServer(
  (req, res) => {
    requests += 1;
    req.resume();
    res.writeHead(200, { "content-type": "application/json" });
    res.end("not json");
  },
  async (port) => {
    await assert.rejects(
      requestJson(`http://127.0.0.1:${port}/`, { headers: {}, body: {}, timeoutMs: 5000, config, retry: true }),
      /不是有效 JSON/
    );
    assert.equal(requests, 1);
  }
);

// A Retry-After beyond retryMaxWait means "not now": one request, no clamped retries.
requests = 0;
await withServer(
  (req, res) => {
    requests += 1;
    req.resume();
    res.writeHead(429, { "content-type": "text/plain", "retry-after": "3600" });
    res.end("slow down");
  },
  async (port) => {
    let caught;
    await assert.rejects(
      requestJson(`http://127.0.0.1:${port}/`, { headers: {}, body: {}, timeoutMs: 5000, config, retry: true }).catch((error) => {
        caught = error;
        throw error;
      }),
      /HTTP 429/
    );
    assert.equal(requests, 1);
    assert.equal(caught.retryAfterMs, 3_600_000);
    assert.equal(caught.retryAfterExceeded, true);
  }
);

// A Retry-After inside the budget is honored and retried.
requests = 0;
await withServer(
  (req, res) => {
    requests += 1;
    req.resume();
    res.writeHead(429, { "content-type": "text/plain", "retry-after": "0" });
    res.end("slow down");
  },
  async (port) => {
    await assert.rejects(
      requestJson(`http://127.0.0.1:${port}/`, { headers: {}, body: {}, timeoutMs: 5000, config, retry: true }),
      /HTTP 429/
    );
    assert.equal(requests, 3);
  }
);

// Firecrawl puts the wait in the body (retry_after_seconds) with a reason; a day-long wait
// stops at once and both fields are surfaced on the error.
requests = 0;
await withServer(
  (req, res) => {
    requests += 1;
    req.resume();
    res.writeHead(429, { "content-type": "application/json" });
    res.end(
      JSON.stringify({
        success: false,
        error: "You've hit Firecrawl's keyless free tier rate limit.",
        reason: "credits",
        retry_after_seconds: 86361,
      })
    );
  },
  async (port) => {
    let caught;
    await assert.rejects(
      requestJson(`http://127.0.0.1:${port}/`, { headers: {}, body: {}, timeoutMs: 5000, config, retry: true }).catch((error) => {
        caught = error;
        throw error;
      }),
      /HTTP 429/
    );
    assert.equal(requests, 1);
    assert.equal(caught.retryAfterMs, 86_361_000);
    assert.equal(caught.upstreamCode, "credits");
    assert.match(caught.upstreamMessage, /keyless free tier/);
  }
);

// Firecrawl's per-minute limiter (seen live 2026-09-08 with an API key) has neither a header nor
// a retry_after_seconds field, only "please retry after 15s" in the message. 15s is beyond this
// config's retry budget, so one request and an honest stop; no reason field, so not a quota hit.
requests = 0;
await withServer(
  (req, res) => {
    requests += 1;
    req.resume();
    res.writeHead(429, { "content-type": "application/json" });
    res.end(
      JSON.stringify({
        success: false,
        error:
          "Rate limit exceeded. Consumed (req/min): 13, Remaining (req/min): 0. Upgrade your plan at https://firecrawl.dev/pricing for increased rate limits or please retry after 15s, resets at Tue Sep 08 2026 03:16:17 GMT+0000 (Coordinated Universal Time)",
      })
    );
  },
  async (port) => {
    let caught;
    await assert.rejects(
      requestJson(`http://127.0.0.1:${port}/`, { headers: {}, body: {}, timeoutMs: 5000, config, retry: true }).catch((error) => {
        caught = error;
        throw error;
      }),
      /HTTP 429/
    );
    assert.equal(requests, 1);
    assert.equal(caught.retryAfterMs, 15_000);
    assert.equal(caught.retryAfterExceeded, true);
    assert.equal(caught.upstreamCode, null);
  }
);

// `stats.requests` counts the HTTP attempts actually made.
requests = 0;
await withServer(
  (req, res) => {
    requests += 1;
    req.resume();
    res.writeHead(503, { "content-type": "text/plain" });
    res.end("down");
  },
  async (port) => {
    const stats = { requests: 0 };
    await assert.rejects(
      requestJson(`http://127.0.0.1:${port}/`, { headers: {}, body: {}, timeoutMs: 5000, config, retry: true, stats }),
      /HTTP 503/
    );
    assert.equal(requests, 3);
    assert.equal(stats.requests, 3);
  }
);

// Timed-out POSTs may still bill server-side; retryOnTimeout=false stops after one attempt.
requests = 0;
await withServer(
  (req) => {
    requests += 1;
    req.resume();
  },
  async (port) => {
    await assert.rejects(
      requestJson(`http://127.0.0.1:${port}/`, {
        headers: {},
        body: {},
        timeoutMs: 200,
        config,
        retry: true,
        retryOnTimeout: false,
      }),
      /请求超时/
    );
    assert.equal(requests, 1);
  }
);

// Default behavior still retries timeouts.
requests = 0;
await withServer(
  (req) => {
    requests += 1;
    req.resume();
  },
  async (port) => {
    await assert.rejects(
      requestJson(`http://127.0.0.1:${port}/`, { headers: {}, body: {}, timeoutMs: 150, config, retry: true }),
      /请求超时/
    );
    assert.equal(requests, 3);
  }
);

// Every channel that talks to a slow search API must pass retryOnTimeout:false, or three 90s
// timeouts overrun the 240s command deadline and the run reports DEADLINE_EXCEEDED instead of
// naming the slow channel — discarding a Grok answer that was already paid for. A real 90s
// timeout is too slow for a test, so this asserts the call sites themselves: any requestJson
// call in a channel module that retries must also disable timeout retries.
{
  const callSites = (source) => {
    const sites = [];
    let from = 0;
    for (;;) {
      const at = source.indexOf("requestJson(", from);
      if (at === -1) return sites;
      let depth = 0;
      let index = at + "requestJson".length;
      for (; index < source.length; index += 1) {
        if (source[index] === "(") depth += 1;
        else if (source[index] === ")") {
          depth -= 1;
          if (depth === 0) {
            index += 1;
            break;
          }
        }
      }
      sites.push(source.slice(at, index));
      from = index;
    }
  };

  for (const file of ["firecrawl.js", "grok-responses.js"]) {
    const source = await readFile(new URL(`../scripts/lib/${file}`, import.meta.url), "utf8");
    for (const site of callSites(source)) {
      if (!/retry:\s*true/.test(site)) continue;
      assert.match(site, /retryOnTimeout:\s*false/, `${file}: a retrying channel call must disable timeout retries`);
    }
  }

  // Tavily builds its options once and spreads them into each call, so check the builder.
  const tavily = await readFile(new URL("../scripts/lib/tavily.js", import.meta.url), "utf8");
  const builder = tavily.slice(tavily.indexOf("function tavilyRequestOptions"));
  assert.match(builder.slice(0, builder.indexOf("\n}")), /retryOnTimeout:\s*false/);
  for (const site of callSites(tavily)) {
    if (!site.includes("tavilyRequestOptions(")) continue;
    assert.match(site, /\.\.\.tavilyRequestOptions\(/, "every Tavily call spreads the shared options");
  }
}

console.log("retry fixtures ok");
