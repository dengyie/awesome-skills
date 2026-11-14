/**
 * Provider orchestration: which service fetches or maps a URL, in what order, and how a
 * failure of one hands over to the next. The adapters live in their own modules
 * (`http.js`, `tavily.js`, `firecrawl.js`, `direct.js`); everything they export is re-exported
 * here so callers keep a single import path.
 */
import { activeExaCooldown, clearExaCooldown, cooldownSkipMessage } from "./cooldown.js";
import { DEFAULT_PROVIDER_WEIGHTS } from "./config.js";
import { directFetch, directFirstForX, directMap, validateXPostContent } from "./direct.js";
import { exaExtract, hasExaApiKey } from "./exa.js";
import { fathomSearch, hasFathomApiKey } from "./fathom.js";
import { firecrawlAuthMode, firecrawlScrape, firecrawlChannelCooldown } from "./firecrawl.js";
import { hasMcpTavily, mcpTavilySearch } from "./mcp-tavily.js";
import { parseXPostUrl } from "./sources.js";
import { hasTavilyApiKey, tavilyExtract, tavilyMap } from "./tavily.js";

export { authHeaders, backoffMs, debugLog, redactSecrets, requestJson, retryAfterMs, retryMaxAttempts, upstreamMessage } from "./http.js";
export {
  allTavilyKeys,
  hasTavilyApiKey,
  hasTavilyProxy,
  isTavilyKeyExhaustedError,
  loadTavilyRoundRobinIndex,
  nextTavilyApiKey,
  saveTavilyRoundRobinIndex,
  sourceFromTavily,
  tavilyExtract,
  tavilyMap,
  tavilyProxyTimeoutMs,
  tavilyRoundRobinPath,
  tavilySearch,
  withTavilyApiKey,
} from "./tavily.js";
export {
  allFirecrawlKeys,
  firecrawlAuthMode,
  firecrawlChannelCooldown,
  firecrawlKeyFingerprint,
  firecrawlMetadata,
  firecrawlRoundRobinPath,
  firecrawlScrape,
  firecrawlSearch,
  hasFirecrawlApiKey,
  isFirecrawlKeySpentError,
  isFirecrawlQuotaError,
  loadFirecrawlRoundRobinIndex,
  nextFirecrawlApiKey,
  saveFirecrawlRoundRobinIndex,
  withFirecrawlApiKey,
} from "./firecrawl.js";
export { exaExtract, exaSearch, hasExaApiKey, isExaQuotaError } from "./exa.js";
export { fathomSearch, hasFathomApiKey } from "./fathom.js";
export { hasMcpTavily, mcpTavilySearch } from "./mcp-tavily.js";
export {
  DIRECT_MAP_REQUEST_TIMEOUT_SECONDS,
  collapseRepeatedLines,
  directFetch,
  directFirstForX,
  directMap,
  validateXPostContent,
  xDirectFirstEligible,
} from "./direct.js";

function summarizeMapFailure(tried, fallback) {
  const details = tried
    .filter((item) => item.error)
    .map((item) => `${item.provider}: ${item.error}`)
    .join("; ");
  return details ? `映射失败: ${details}` : fallback || "映射失败";
}

function attemptFromResult(result) {
  return {
    provider: result.provider,
    ok: result.ok,
    skipped: Boolean(result.skipped),
    error: result.error,
    ...(result.tavily_backend ? { tavily_backend: result.tavily_backend } : {}),
    ...(Number.isFinite(result.tavily_key_index) ? { tavily_key_index: result.tavily_key_index } : {}),
    ...(result.tavily_proxy_tried ? { tavily_proxy_tried: true } : {}),
    ...(result.tavily_proxy_error ? { tavily_proxy_error: result.tavily_proxy_error } : {}),
  };
}

/**
 * How many results each extra channel should ask for.
 *
 * Every configured channel searches the full target; mergeSources then dedupes the union.
 * Search endpoints bill per request, not per result, so this costs the same requests as a
 * split allocation while giving the merge step the most candidates to dedupe against. A
 * missing key or an active cooldown drops that channel entirely.
 *
 * `providerWeights` scales the per-channel target: a weight of 0 switches a channel off
 * entirely, and weights below 1 shrink its request (fewer results, same one request).
 * Weights above 1 cannot buy more than the target, since the target is what the caller
 * asked for in total.
 */
export function extraAllocation(limit, config, { firecrawlAvailable = true, exaAvailable = true, fathomAvailable = true, mcpTavilyAvailable = true } = {}) {
  if (limit <= 0) return emptyAllocation();

  // A config without providerWeights means "every channel at its full share". Falling back to
  // the defaults keeps a hand-built config (tests, embedders) from silently switching every
  // channel off.
  const weights = { ...DEFAULT_PROVIDER_WEIGHTS, ...(config?.providerWeights || {}) };
  const scale = (channel) => {
    const weight = Number(weights[channel]);
    if (!Number.isFinite(weight) || weight <= 0) return 0;
    // A weight of 1 means the full target; smaller weights ask for proportionally fewer
    // results, but never fewer than one (a request for 0 results is a wasted request).
    if (weight >= 1) return limit;
    return Math.max(1, Math.round(limit * weight));
  };

  return {
    tavily: hasTavilyApiKey(config) ? scale("tavily") : 0,
    firecrawl: firecrawlAvailable ? scale("firecrawl") : 0,
    exa: exaAvailable && hasExaApiKey(config) ? scale("exa") : 0,
    fathom: fathomAvailable && hasFathomApiKey(config) ? scale("fathom") : 0,
    mcpTavily: mcpTavilyAvailable && hasMcpTavily(config) ? scale("mcpTavily") : 0,
  };
}

/** The allocation shape with every channel switched off. */
export function emptyAllocation() {
  return { tavily: 0, firecrawl: 0, exa: 0, fathom: 0, mcpTavily: 0 };
}

export async function mapUrl(url, config, { provider = "auto", ...options } = {}) {
  const tried = [];

  if (provider === "direct") {
    const result = await directMap(url, options);
    tried.push({ provider: result.provider, ok: result.ok, skipped: false, error: result.error });
    return { ...result, tried };
  }

  if (provider === "auto" || provider === "tavily") {
    const result = await tavilyMap(url, options, config);
    tried.push(attemptFromResult(result));
    if (result.ok || provider === "tavily") return { ...result, tried };
  }

  if (provider === "auto") {
    const result = await directMap(url, options);
    tried.push({ provider: result.provider, ok: result.ok, skipped: false, error: result.error });
    if (result.ok) return { ...result, tried };
    return { ...result, tried, error: summarizeMapFailure(tried, result.error) };
  }

  return { ok: false, provider, results: [], tried, error: `未知 provider: ${provider}` };
}

function summarizeFetchFailure(tried, fallback) {
  const details = tried
    .filter((item) => item.error)
    .map((item) => `${item.provider}: ${item.error}`)
    .join("; ");
  return details ? `提取失败: ${details}` : fallback || "提取失败: 所有提取服务均未能获取内容";
}

export async function fetchUrl(url, config, { provider = "auto", maxChars } = {}) {
  const tried = [];
  let directFirst = null;

  if (provider === "direct") {
    const result = await directFetch(url);
    tried.push({ provider: result.provider, ok: result.ok, skipped: false, error: result.error });
    return { ...result, tried };
  }

  const xPost = directFirstForX(url, config, provider);
  if (xPost) {
    const result = await directFetch(url);
    // X redirects /<anyhandle>/status/<id> to the post's real handle, so the page names
    // the canonical handle, not the one in the requested URL. Validate against the former.
    const finalPost = result.ok ? parseXPostUrl(result.final_url || url) : null;
    const post = finalPost?.x_handle && finalPost.x_post_id === xPost.x_post_id ? finalPost : xPost;
    const validation = result.ok ? validateXPostContent(result.content, post) : { ok: false, missing: [] };
    if (result.ok && validation.ok) {
      tried.push({
        provider: "direct",
        ok: true,
        skipped: false,
        x_validated: true,
        ...(post.x_handle !== xPost.x_handle ? { x_handle: post.x_handle } : {}),
      });
      return { ...result, tried };
    }
    directFirst = result;
    tried.push({
      provider: "direct",
      ok: false,
      skipped: false,
      error: result.ok ? `x_validation_failed: ${validation.missing.join(",")}` : result.error,
    });
  }

  if (provider === "auto" || provider === "tavily") {
    const result = await tavilyExtract(url, config);
    tried.push(attemptFromResult(result));
    if (result.ok || provider === "tavily") return { ...result, tried };
  }

  if (provider === "auto" || provider === "firecrawl") {
    const authMode = firecrawlAuthMode(config);
    // An explicit --provider firecrawl still makes the request: the user may have just added
    // a key or topped up, and a success clears the stale cooldown.
    // With a key pool the channel is only dead when every key is cooling; one spent key is
    // skipped inside the pool instead of switching the whole channel off.
    const cooldown = provider === "auto" ? await firecrawlChannelCooldown(config) : null;
    if (cooldown) {
      tried.push({ provider: "firecrawl", ok: false, skipped: true, auth_mode: authMode, error: cooldownSkipMessage(cooldown) });
    } else {
      const result = await firecrawlScrape(url, config);
      tried.push({
        provider: result.provider,
        ok: result.ok,
        skipped: Boolean(result.skipped),
        error: result.error,
        auth_mode: result.auth_mode,
        ...(result.requests == null ? {} : { requests: result.requests }),
        ...(result.duration_ms == null ? {} : { duration_ms: result.duration_ms }),
        ...(result.credits_used == null ? {} : { credits_used: result.credits_used }),
        ...(result.firecrawl_key_index == null ? {} : { firecrawl_key_index: result.firecrawl_key_index }),
        ...(result.firecrawl_key_total == null ? {} : { firecrawl_key_total: result.firecrawl_key_total }),
        ...(result.firecrawl_keys_tried == null ? {} : { firecrawl_keys_tried: result.firecrawl_keys_tried }),
      });
      if (result.ok || provider === "firecrawl") return { ...result, tried };
    }
  }

  if (provider === "auto" || provider === "exa") {
    // A cooldown only spares an empty balance; an explicit --provider exa still makes the
    // request so a topped-up key clears the stale state.
    const cooldown = provider === "auto" ? await activeExaCooldown(config) : null;
    if (cooldown) {
      tried.push({ provider: "exa", ok: false, skipped: true, error: cooldownSkipMessage(cooldown) });
    } else {
      const result = await exaExtract(url, config, { maxChars });
      tried.push({
        provider: result.provider,
        ok: result.ok,
        skipped: Boolean(result.skipped),
        error: result.error,
        ...(result.requests == null ? {} : { requests: result.requests }),
        ...(result.duration_ms == null ? {} : { duration_ms: result.duration_ms }),
        ...(result.cost_usd == null ? {} : { cost_usd: result.cost_usd }),
      });
      if (result.ok && provider === "exa") await clearExaCooldown(config);
      if (result.ok || provider === "exa") return { ...result, tried };
    }
  }

  if (provider === "auto") {
    if (directFirst) {
      // Direct already ran for this X post. Its page did not validate, but with nothing else
      // available it is still better than an error; say so instead of fetching it again.
      if (directFirst.ok) {
        const failed = tried.find((attempt) => attempt.provider === "direct" && !attempt.ok);
        const warning = `Direct 抓到的 X 页面未通过原帖校验（${failed?.error || "x_validation_failed"}），其他 provider 不可用，按原样返回；需要完整帖文或 thread 时用 --provider firecrawl。`;
        tried.push({ provider: "direct", ok: true, skipped: false, reused: true });
        return { ...directFirst, warnings: [...(directFirst.warnings || []), warning], tried };
      }
      return { ...directFirst, tried, error: summarizeFetchFailure(tried, directFirst.error) };
    }
    const result = await directFetch(url);
    tried.push({ provider: result.provider, ok: result.ok, skipped: false, error: result.error });
    if (result.ok) return { ...result, tried };
    return { ...result, tried, error: summarizeFetchFailure(tried, result.error) };
  }

  return { ok: false, provider, tried, error: `未知 provider: ${provider}` };
}
