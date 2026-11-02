/** Independent Tavily / Firecrawl / Exa extra searches: allocation, fan-out, and attempt shaping. */
import { activeExaCooldown, activeFirecrawlCooldown, cooldownSkipMessage } from "./cooldown.js";
import { usesWebSearch, usesXSearch } from "./config.js";
import { exaSearch } from "./exa.js";
import { firecrawlAuthMode, firecrawlSearch } from "./firecrawl.js";
import { extraAllocation } from "./providers.js";
import { isOffDomainExtra } from "./sources.js";
import { tavilySearch } from "./tavily.js";

function providerAttempt(result) {
  return {
    provider: result.provider,
    ok: Boolean(result.ok),
    count: result.sources?.length || 0,
    ...(result.skipped ? { skipped: true } : {}),
    ...(result.auth_mode ? { auth_mode: result.auth_mode } : {}),
    ...(result.credits_used == null ? {} : { credits_used: result.credits_used }),
    ...(Number.isFinite(result.cost_usd) ? { cost_usd: result.cost_usd } : {}),
    ...(Number.isFinite(result.requests) ? { requests: result.requests } : {}),
    ...(Number.isFinite(result.duration_ms) ? { duration_ms: result.duration_ms } : {}),
    ...(result.quota_exhausted ? { quota_exhausted: true } : {}),
    ...(result.tavily_backend ? { tavily_backend: result.tavily_backend } : {}),
    ...(Number.isFinite(result.tavily_key_index) ? { tavily_key_index: result.tavily_key_index } : {}),
    ...(result.tavily_proxy_tried ? { tavily_proxy_tried: true } : {}),
    ...(result.tavily_proxy_error ? { tavily_proxy_error: result.tavily_proxy_error } : {}),
    ...(result.error ? { error: result.error } : {}),
  };
}

/**
 * Independent Tavily / Firecrawl / Exa searches. Domain filters are the same ones Grok's
 * web_search gets: when the caller scopes a search to github.com, extras that wander off to
 * blogs and video sites only displace in-scope candidates. A Firecrawl quota cooldown hands its
 * share to the other channels; the same applies to an Exa balance cooldown.
 */
export async function extraSources(query, limit, config, filters = {}) {
  const warnings = [];
  const providerRaw = {};
  if (limit <= 0) {
    return { sources: [], warnings, provider_attempts: [], provider_raw: providerRaw, allocation: { tavily: 0, firecrawl: 0, exa: 0 } };
  }

  const firecrawlMode = firecrawlAuthMode(config);
  const cooldown = await activeFirecrawlCooldown(config, firecrawlMode);
  const exaCooldown = await activeExaCooldown(config);
  const allocation = extraAllocation(limit, config, { firecrawlAvailable: !cooldown, exaAvailable: !exaCooldown });

  // Timed per provider so the attempt says which side made the caller wait.
  const timed = async (job) => {
    const started = performance.now();
    const result = await job;
    return { ...result, duration_ms: Math.round(performance.now() - started) };
  };
  const jobs = [];
  if (allocation.tavily > 0) jobs.push(timed(tavilySearch(query, allocation.tavily, config, filters)));
  if (allocation.firecrawl > 0) jobs.push(timed(firecrawlSearch(query, allocation.firecrawl, config, filters)));
  if (allocation.exa > 0) jobs.push(timed(exaSearch(query, allocation.exa, config, filters)));
  const results = await Promise.all(jobs);
  const sources = [];
  const providerAttempts = [];

  const hasFilters = Boolean(filters.allowedDomains?.length || filters.excludedDomains?.length);
  for (const result of results) {
    const attempt = providerAttempt(result);
    if (result.ok && hasFilters) {
      attempt.off_domain = (result.sources || []).filter((source) => isOffDomainExtra(source, filters)).length;
    }
    providerAttempts.push(attempt);
    if (result.raw !== undefined) providerRaw[result.provider] = result.raw;
    if (result.ok) sources.push(...(result.sources || []));
    else warnings.push(`${result.provider} extra source search failed: ${result.error || "unknown error"}`);
  }

  if (cooldown) {
    const message = cooldownSkipMessage(cooldown);
    providerAttempts.push({ provider: "firecrawl", ok: false, count: 0, skipped: true, auth_mode: firecrawlMode, error: message });
    warnings.push(`firecrawl extra source search skipped: ${message}`);
  }

  if (exaCooldown) {
    const message = cooldownSkipMessage(exaCooldown);
    providerAttempts.push({ provider: "exa", ok: false, count: 0, skipped: true, error: message });
    warnings.push(`exa extra source search skipped: ${message}`);
  }

  // No cap here: every channel returns up to `limit`, and the union only gets truncated later
  // by selectSources (max_sources) — cutting earlier would discard dedupe candidates.
  return {
    sources,
    warnings,
    provider_attempts: providerAttempts,
    provider_raw: providerRaw,
    allocation,
  };
}

export function resolveExtra(args, config, searchSource) {
  if (args.extraMode === "off") return { limit: 0, mode: "off" };
  if (args.extraMode === "explicit") return { limit: args.extra, mode: "explicit" };
  // Tavily and Firecrawl only search the web. On an X-only search their results are off-topic
  // by construction (6 of 6 in the 2026-09-08 side-by-side) and still bill credits, so they
  // stay off unless the caller asks for them with --extra N.
  if (usesXSearch(searchSource) && !usesWebSearch(searchSource)) return { limit: 0, mode: "off-x-only" };
  return { limit: config.defaultExtra, mode: "auto" };
}

export function extraModeWarnings(extraOptions) {
  if (extraOptions.mode !== "off-x-only") return [];
  return ["extra sources skipped: --source x searches X only and Tavily/Firecrawl/Exa search the web; pass --extra N to include them."];
}
