import { recordExaCooldown } from "./cooldown.js";
import { debugLog, requestJson } from "./http.js";
import { domainFilters } from "./sources.js";

export function hasExaApiKey(config) {
  return Boolean(config?.exaApiKey);
}

/**
 * Exa answers an empty balance with HTTP 402; 429 is normally a burst rate limit, which
 * requestJson already retries, and only counts as quota when the message names credits.
 */
export function isExaQuotaError(error) {
  if (error?.status === 402) return true;
  return error?.status === 429 && /credit|quota|balance|余额/i.test(String(error?.message || ""));
}

function exaHeaders(config) {
  return { "Content-Type": "application/json", "x-api-key": config.exaApiKey };
}

/**
 * The first non-empty highlight is the page's most query-relevant passage, which is what a
 * source card's description wants. `highlightScores` is the only relevance signal Exa returns.
 */
function sourceFromExa(result) {
  const url = typeof result?.url === "string" ? result.url.trim() : "";
  if (!url) return null;
  const highlight = Array.isArray(result.highlights)
    ? result.highlights.find((item) => typeof item === "string" && item.trim())
    : undefined;
  const score = Array.isArray(result.highlightScores)
    ? result.highlightScores.find((value) => Number.isFinite(value))
    : undefined;
  return {
    url,
    provider: "exa",
    ...(result.title ? { title: String(result.title).trim() } : {}),
    ...(highlight ? { description: highlight.trim() } : {}),
    ...(result.publishedDate ? { published_date: String(result.publishedDate).trim() } : {}),
    ...(Number.isFinite(score) ? { score } : {}),
  };
}

export async function exaSearch(query, limit, config, filters = {}) {
  if (!hasExaApiKey(config)) {
    return { ok: false, provider: "exa", skipped: true, error: "EXA_API_KEY 未配置", sources: [] };
  }

  const endpoint = `${config.exaApiUrl.replace(/\/+$/, "")}/search`;
  const { allowed, excluded } = domainFilters(filters);
  const startedAt = Date.now();
  const stats = { requests: 0 };
  try {
    const data = await requestJson(endpoint, {
      headers: exaHeaders(config),
      body: {
        query,
        type: "auto",
        // Exa rejects numResults above 100 with INVALID_REQUEST_BODY; a large --extra
        // would kill the whole channel for the run, so cap at the documented maximum.
        numResults: Math.min(limit, 100),
        contents: { highlights: true },
        // includeDomains/excludeDomains accept hostnames, host+path and *.wildcard — the same
        // filter pair Tavily/Firecrawl get.
        ...(allowed.length ? { includeDomains: allowed } : {}),
        ...(excluded.length ? { excludeDomains: excluded } : {}),
      },
      timeoutMs: 60_000,
      config,
      retry: true,
      stats,
    });
    const rawResults = Array.isArray(data?.results) ? data.results : [];
    return {
      ok: true,
      provider: "exa",
      sources: rawResults.map(sourceFromExa).filter(Boolean),
      raw: data,
      requests: stats.requests,
      duration_ms: Date.now() - startedAt,
      ...(Number.isFinite(data?.costDollars?.total) ? { cost_usd: data.costDollars.total } : {}),
    };
  } catch (error) {
    const quota = isExaQuotaError(error);
    if (quota) {
      await recordExaCooldown(config, { retryAfterMs: error.retryAfterMs, reason: error.upstreamCode || "quota" });
    }
    return {
      ok: false,
      provider: "exa",
      error: error.message,
      sources: [],
      requests: stats.requests,
      duration_ms: Date.now() - startedAt,
      ...(quota ? { quota_exhausted: true } : {}),
    };
  }
}

function exaMetadata(result, url) {
  const meta = { source_url: url };
  if (result?.title) meta.title = String(result.title).trim();
  if (result?.author) meta.author = String(result.author).trim();
  if (result?.publishedDate) meta.published_at = String(result.publishedDate).trim();
  return meta;
}

export async function exaExtract(url, config, { maxChars = 12_000, timeoutMs = 60_000 } = {}) {
  if (!hasExaApiKey(config)) {
    return { ok: false, provider: "exa", skipped: true, error: "EXA_API_KEY 未配置" };
  }

  const endpoint = `${config.exaApiUrl.replace(/\/+$/, "")}/contents`;
  const startedAt = Date.now();
  const stats = { requests: 0 };
  const fail = (error, extra = {}) => ({
    ok: false,
    provider: "exa",
    error,
    requests: stats.requests,
    duration_ms: Date.now() - startedAt,
    ...extra,
  });

  let data;
  try {
    data = await requestJson(endpoint, {
      headers: exaHeaders(config),
      body: { urls: [url], text: { maxCharacters: maxChars } },
      timeoutMs,
      config,
      retry: true,
      stats,
    });
  } catch (error) {
    const quota = isExaQuotaError(error);
    if (quota) {
      await recordExaCooldown(config, { retryAfterMs: error.retryAfterMs, reason: error.upstreamCode || "quota" });
    }
    return fail(error.message, quota ? { quota_exhausted: true } : {});
  }

  const statuses = Array.isArray(data?.statuses) ? data.statuses : [];
  const status = statuses.find((item) => item?.id === url) || statuses[0];
  if (status && status.status && status.status !== "success") {
    return fail(`Exa Contents 抓取失败（${status.status}）`);
  }

  const result = (Array.isArray(data?.results) ? data.results : [])[0];
  const content = typeof result?.text === "string" ? result.text : "";
  if (!content.trim()) {
    debugLog(config, "Exa Contents 返回空内容");
    return fail("Exa Contents 返回空内容");
  }

  return {
    ok: true,
    provider: "exa",
    content,
    raw: data,
    requests: stats.requests,
    duration_ms: Date.now() - startedAt,
    metadata: exaMetadata(result, url),
    ...(Number.isFinite(data?.costDollars?.total) ? { cost_usd: data.costDollars.total } : {}),
  };
}
