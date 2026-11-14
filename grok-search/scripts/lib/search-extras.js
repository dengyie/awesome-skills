/** Independent Tavily / Firecrawl / Exa / fathom / MCP-Tavily extra searches: allocation, fan-out, and attempt shaping. */
import {
  activeChannelCooldown,
  activeExaCooldown,
  cooldownSkipMessage,
} from "./cooldown.js";
import { usesWebSearch, usesXSearch } from "./config.js";
import { exaSearch } from "./exa.js";
import { fathomSearch } from "./fathom.js";
import { firecrawlAuthMode, firecrawlChannelCooldown, firecrawlSearch } from "./firecrawl.js";
import { mcpTavilySearch } from "./mcp-tavily.js";
import { emptyAllocation, extraAllocation } from "./providers.js";
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
    ...(Number.isFinite(result.firecrawl_key_index) ? { firecrawl_key_index: result.firecrawl_key_index } : {}),
    ...(Number.isFinite(result.firecrawl_key_total) ? { firecrawl_key_total: result.firecrawl_key_total } : {}),
    ...(Number.isFinite(result.firecrawl_keys_tried) ? { firecrawl_keys_tried: result.firecrawl_keys_tried } : {}),
    ...(result.error ? { error: result.error } : {}),
  };
}

/**
 * Independent Tavily / Firecrawl / Exa / fathom / MCP-Tavily searches. Domain filters are
 * the same ones Grok's web_search gets: when the caller scopes a search to github.com,
 * extras that wander off to blogs and video sites only displace in-scope candidates. A
 * Firecrawl quota cooldown hands its share to the other channels; the same applies to an
 * Exa balance cooldown and to an MCP channel that is in cooldown.
 */
export async function extraSources(query, limit, config, filters = {}) {
  const warnings = [];
  const providerRaw = {};
  if (limit <= 0) {
    return { sources: [], warnings, provider_attempts: [], provider_raw: providerRaw, allocation: emptyAllocation() };
  }

  const firecrawlMode = firecrawlAuthMode(config);
  // With a key pool the channel is only dead when every key is cooling; one spent key is
  // skipped inside the pool instead of switching the whole channel off.
  const cooldown = await firecrawlChannelCooldown(config);
  const exaCooldown = await activeExaCooldown(config);
  // The MCP channels key their cooldown on the server URL, so a different relay takes
  // effect immediately instead of waiting out the old cooldown.
  const fathomCooldown = await activeChannelCooldown(config, "fathom", config.fathomApiUrl);
  const mcpTavilyCooldown = await activeChannelCooldown(config, "mcpTavily", config.mcpTavilyUrl);
  const allocation = extraAllocation(limit, config, {
    firecrawlAvailable: !cooldown,
    exaAvailable: !exaCooldown,
    fathomAvailable: !fathomCooldown,
    mcpTavilyAvailable: !mcpTavilyCooldown,
  });

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
  if (allocation.fathom > 0) jobs.push(timed(fathomSearch(query, allocation.fathom, config, filters)));
  if (allocation.mcpTavily > 0) jobs.push(timed(mcpTavilySearch(query, allocation.mcpTavily, config, filters)));
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

  if (fathomCooldown) {
    const message = cooldownSkipMessage(fathomCooldown);
    providerAttempts.push({ provider: "fathom", ok: false, count: 0, skipped: true, error: message });
    warnings.push(`fathom extra source search skipped: ${message}`);
  }

  if (mcpTavilyCooldown) {
    const message = cooldownSkipMessage(mcpTavilyCooldown);
    providerAttempts.push({ provider: "mcpTavily", ok: false, count: 0, skipped: true, error: message });
    warnings.push(`mcpTavily extra source search skipped: ${message}`);
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
