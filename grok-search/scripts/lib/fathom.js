/**
 * fathom extra search channel.
 *
 * fathom is an MCP server that fans one query out across several web engines (brave,
 * google, bing, duckduckgo, baidu, ...). It is configured in config.json as
 * `fathomApiUrl` + `fathomApiKey` + `fathomSearchTool`; the tool name defaults to
 * `mega_search` but `search` (one engine) is the more reliable variant here.
 *
 * Engine health is not constant: `list_engines` reports a per-engine circuit breaker, and
 * an engine that is `open` fails the whole call when it is the only one requested. The
 * adapter therefore treats the configured engine list as a preference and falls back to
 * the server's own default routing when the preferred call fails.
 */
import { recordChannelCooldown } from "./cooldown.js";
import { debugLog } from "./http.js";
import { hasMcpConfig, mcpSearch } from "./mcp.js";

/**
 * Total time budget for one fathom search, across every engine plan.
 *
 * The adapter retries plans in sequence (configured engines, then each single engine, then the
 * fallbacks), so a per-plan timeout multiplies: at 90s each, a cold server could run for minutes
 * and outlast the command's own deadline, killing a search that already had an answer from Grok.
 * One budget for the whole call keeps this channel as expensive as any other single extra.
 */
const FATHOM_TIMEOUT_MS = 45_000;

function fathomBudgetMs(config) {
  const configured = config?.fathomTimeoutMs;
  if (Number.isInteger(configured) && configured >= 1) return configured;
  return FATHOM_TIMEOUT_MS;
}

/**
 * Engines that were observed working at the server. `list_engines` reports a per-engine
 * circuit breaker, and an engine that is `open` fails the whole call. Ordered by observed
 * latency: `bing` answers in about a second, while `duckduckgo` can sit on a server-side
 * timeout for a minute and a half before failing.
 */
const FALLBACK_ENGINES = ["bing", "duckduckgo"];

const ENGINES_PROBE_TIMEOUT_MS = 5_000;
// Floor for a single plan so the share never collapses to a few milliseconds.
const FATHOM_MIN_PLAN_MS = 5_000;

/**
 * Names of the engines the server still considers healthy (breaker closed), or null when the
 * probe is unavailable or every engine is open — in that case the caller keeps the legacy plan
 * order instead of guessing.
 */
async function probeHealthyEngines(url, token, config, startedAt) {
  const budgetLeft = fathomBudgetMs(config) - (Date.now() - startedAt);
  const timeoutMs = Math.max(200, Math.min(ENGINES_PROBE_TIMEOUT_MS, budgetLeft));
  try {
    const payload = await mcpSearch(url, token, "list_engines", {}, { timeoutMs, config });
    const list = Array.isArray(payload?.engines) ? payload.engines : null;
    if (!list) return null;
    const closed = list
      .filter((engine) => engine?.circuit_state === "closed")
      .map((engine) => String(engine?.name || "").trim())
      .filter(Boolean);
    return closed.length ? new Set(closed) : null;
  } catch (error) {
    debugLog(config, `fathom list_engines probe failed: ${error.message}`);
    return null;
  }
}

export function hasFathomApiKey(config) {
  return hasMcpConfig(config, { urlKey: "fathomApiUrl", tokenKey: "fathomApiKey" });
}

function fathomUrl(config) {
  return String(config?.fathomApiUrl || "").trim();
}

function fathomTool(config) {
  const tool = String(config?.fathomSearchTool || "").trim();
  return tool || "mega_search";
}

function fathomEngines(config) {
  const engines = String(config?.fathomEngines || "").trim();
  if (!engines) return [];
  return engines
    .split(",")
    .map((engine) => engine.trim())
    .filter(Boolean);
}

/** A fathom result carries a title, a URL and a snippet; the snippet is the description. */
function sourceFromFathom(result) {
  const url = typeof result?.url === "string" ? result.url.trim() : "";
  if (!url) return null;
  const snippet = typeof result?.snippet === "string" ? result.snippet.trim() : "";
  const title = typeof result?.title === "string" ? result.title.trim() : "";
  return {
    url,
    provider: "fathom",
    ...(title ? { title } : {}),
    ...(snippet ? { description: snippet } : {}),
  };
}

function fathomResults(payload) {
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload?.items)) return payload.items;
  return [];
}

/**
 * Search through fathom. `limit` is the per-channel target; fathom returns a page of
 * results, so the list is trimmed to the target after the call.
 *
 * The call plan matters more than it looks. `mega_search` fans out to every engine in
 * `engines` and fails the whole call (`all_engines_failed`) when any one of them is
 * unhealthy — and the engines' health is a per-server circuit breaker, so one flaky engine
 * takes down a query that another engine could have answered. It also waits for the slowest
 * engine in the list, which is why the fan-out runs last. `search` takes exactly one engine
 * and fails only for that engine, so the reliable shape is: `list_engines` to learn which
 * breakers are closed, then one engine at a time (configured engines first, then the engines
 * observed to work), then the fan-out over the healthy ones as a last resort.
 */
export async function fathomSearch(query, limit, config, filters = {}) {
  if (!hasFathomApiKey(config)) {
    return { ok: false, provider: "fathom", skipped: true, error: "FATHOM_API_KEY 未配置", sources: [] };
  }

  const url = fathomUrl(config);
  const token = String(config?.fathomApiKey || "").trim();
  const tool = fathomTool(config);
  const engines = fathomEngines(config);
  const startedAt = Date.now();

  // fathom's `search` tool takes one engine; `mega_search` takes a list. The
  // configured tool decides which argument shape applies.
  const buildArgs = (engineList) => {
    const args = { text: query, limit: Math.max(1, Math.min(limit, 20)) };
    if (engineList) args.engines = engineList;
    return args;
  };

  const attempts = [];
  // Ask the server which engines it considers healthy. Without this the first plan fans out
  // over every engine including the ones whose breaker is open, and the server answers only
  // after its own slowest engine times out (observed: 85s, then `all_engines_failed`).
  const healthy = await probeHealthyEngines(url, token, config, startedAt);
  const isHealthy = (engine) => !healthy || healthy.has(engine);

  const plans = [];
  if (!healthy) {
    // Probe unavailable: keep the previous order (fan-out first) rather than guessing health.
    if (engines.length) plans.push({ tool, args: buildArgs(engines.join(",")) });
    for (const engine of engines) plans.push({ tool, args: buildArgs(engine) });
  }
  // Single engines before the fan-out: one engine answers (or fails) on its own, while the
  // fan-out always waits for the slowest engine in the list, so it belongs last.
  for (const engine of engines.filter(isHealthy)) plans.push({ tool, args: buildArgs(engine) });
  for (const engine of FALLBACK_ENGINES) {
    if (engines.includes(engine) || !isHealthy(engine)) continue;
    plans.push({ tool, args: buildArgs(engine) });
  }
  if (healthy) {
    const fanOut = [...new Set([...engines, ...FALLBACK_ENGINES])].filter(isHealthy);
    if (fanOut.length) plans.push({ tool, args: buildArgs(fanOut.join(",")) });
  }

  let lastError = null;
  const deadlineAt = startedAt + fathomBudgetMs(config);
  for (const [index, plan] of plans.entries()) {
    const remaining = deadlineAt - Date.now();
    if (remaining <= 0) {
      attempts.push(`预算用尽（${Math.round((Date.now() - startedAt) / 1000)}s），剩余方案跳过`);
      break;
    }
    // Each plan gets a share of what is left, not all of it: a plan that hangs until the
    // deadline would consume the budget and leave the remaining engines untried.
    const planTimeout = Math.min(remaining, Math.max(FATHOM_MIN_PLAN_MS, Math.floor(remaining / (plans.length - index))));
    try {
      const payload = await mcpSearch(url, token, plan.tool, plan.args, {
        timeoutMs: planTimeout,
        config,
      });
      const results = fathomResults(payload);
      if (!results.length) {
        attempts.push(`${plan.tool}(${plan.args.engines || "default"}): 返回空结果`);
        continue;
      }
      return {
        ok: true,
        provider: "fathom",
        sources: results.map(sourceFromFathom).filter(Boolean).slice(0, limit),
        raw: payload,
        duration_ms: Date.now() - startedAt,
        fathom_tool: plan.tool,
        ...(plan.args.engines ? { fathom_engines: plan.args.engines } : {}),
      };
    } catch (error) {
      lastError = error;
      attempts.push(`${plan.tool}(${plan.args.engines || "default"}): ${error.message}`);
      debugLog(config, `fathom attempt failed: ${error.message}`);
    }
  }

  // Every plan failed. A 5xx or a timeout means the relay is unhealthy, so a cooldown
  // keeps later commands from paying for the same failure.
  if (lastError && (lastError.status >= 500 || lastError.timedOut || lastError.status === 401 || lastError.status === 403)) {
    await recordChannelCooldown(config, "fathom", {
      authMode: url,
      reason: lastError.status ? `http_${lastError.status}` : "timeout",
    });
  }

  return {
    ok: false,
    provider: "fathom",
    error: attempts.join("; ") || "Fathom 搜索失败",
    sources: [],
    duration_ms: Date.now() - startedAt,
  };
}
