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

const FATHOM_TIMEOUT_MS = 90_000;

/**
 * Engines that were observed working at the server. `list_engines` reports a per-engine
 * circuit breaker, and an engine that is `open` fails the whole call.
 */
const FALLBACK_ENGINES = ["duckduckgo", "bing"];

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
 * takes down a query that another engine could have answered. `search` takes exactly one
 * engine and fails only for that engine, so the reliable shape is: the configured tool
 * with the configured engines first, then the same tool one engine at a time over the
 * configured list, then the engines observed to work.
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
  const plans = [];
  if (engines.length) {
    plans.push({ tool, args: buildArgs(engines.join(",")) });
    // One engine at a time: a single unhealthy engine no longer fails the whole query.
    for (const engine of engines) plans.push({ tool, args: buildArgs(engine) });
  }
  for (const engine of FALLBACK_ENGINES) {
    if (engines.includes(engine)) continue;
    plans.push({ tool, args: buildArgs(engine) });
  }

  let lastError = null;
  for (const plan of plans) {
    try {
      const payload = await mcpSearch(url, token, plan.tool, plan.args, {
        timeoutMs: FATHOM_TIMEOUT_MS,
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
