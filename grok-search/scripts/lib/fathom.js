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
const FATHOM_TIMEOUT_MS = 30_000;

function fathomBudgetMs(config) {
  const configured = config?.fathomTimeoutMs;
  if (Number.isInteger(configured) && configured >= 1) return configured;
  return FATHOM_TIMEOUT_MS;
}

/**
 * Engines that search the open web, in preference order.
 *
 * This is the server's own answer to what `mega_search` accepts: its `list_engines` also reports
 * single-catalog engines (arxiv, wikipedia, pubmed, github, and several adult image boards), and
 * a mega call naming one of those fails outright — "engine \"arxiv\" is a single-catalog engine and
 * not allowed in mega tools". Leaving them in the candidate list therefore burns the whole plan
 * list on calls the server refuses before a real engine is ever tried.
 *
 * `google` leads because the general-web engines rotate: at one point bing, duckduckgo, brave,
 * ecosia, grok, baidu and yandex were all open while google stayed closed.
 */
const WEB_ENGINES = ["google", "bing", "duckduckgo", "brave", "ecosia", "grok", "baidu", "yandex"];

/**
 * Cap on single-engine attempts. A handful is enough to find one working engine; more would
 * only slice the shared budget thinner.
 */
const MAX_ENGINE_PLANS = 4;

const ENGINES_PROBE_TIMEOUT_MS = 5_000;
// Floor for a single plan so the share never collapses to a few milliseconds.
const FATHOM_MIN_PLAN_MS = 5_000;

/**
 * The engines the server reports as usable, or null when the probe failed. Open and closed
 * names are both kept: the closed ones become the plan, the open ones explain a total failure.
 */
async function probeEngines(url, token, config, startedAt) {
  const budgetLeft = fathomBudgetMs(config) - (Date.now() - startedAt);
  const timeoutMs = Math.max(200, Math.min(ENGINES_PROBE_TIMEOUT_MS, budgetLeft));
  try {
    const payload = await mcpSearch(url, token, "list_engines", {}, { timeoutMs, config });
    const list = Array.isArray(payload?.engines) ? payload.engines : null;
    if (!list) return null;
    const closed = [];
    const open = [];
    for (const engine of list) {
      const name = String(engine?.name || "").trim();
      if (!name) continue;
      (engine?.circuit_state === "closed" ? closed : open).push(name);
    }
    return { closed, open };
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
 * breakers are closed, then one engine at a time from a bounded shortlist (configured engines
 * first, then the general-web set in preference order), then the fan-out over that shortlist as
 * a last resort.
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
  const probe = await probeEngines(url, token, config, startedAt);
  const healthy = probe ? new Set(probe.closed) : null;
  const openEngines = probe ? probe.open : [];

  const plans = [];
  if (!probe) {
    // Probe unavailable: keep the previous order (fan-out first) rather than guessing health.
    if (engines.length) plans.push({ tool, args: buildArgs(engines.join(",")) });
    for (const engine of engines) plans.push({ tool, args: buildArgs(engine) });
    for (const engine of WEB_ENGINES) {
      if (!engines.includes(engine)) plans.push({ tool, args: buildArgs(engine) });
    }
  } else {
    // Candidate order: configured engines first, then the web engines in preference order. Only
    // web engines are planned — a closed catalog engine (arxiv, wikipedia) is not an alternative,
    // because the mega tools reject it and the single-engine `search` tool answers a different
    // question. The configured list is exempt: the user asked for those engine names explicitly.
    const candidates = [];
    for (const engine of [...engines, ...WEB_ENGINES]) {
      if (healthy.has(engine) && !candidates.includes(engine)) candidates.push(engine);
    }
    const shortlist = candidates.slice(0, MAX_ENGINE_PLANS);
    for (const engine of shortlist) plans.push({ tool, args: buildArgs(engine) });
    // The fan-out must stay inside the web set for the same reason: one catalog engine in the
    // list fails the whole call before any web engine runs.
    const fanOut = shortlist.filter((engine) => engines.includes(engine) || WEB_ENGINES.includes(engine));
    if (fanOut.length > 1) plans.push({ tool, args: buildArgs(fanOut.join(",")) });
  }
  // Never leave the channel without a plan. When every preferred engine's breaker is open the
  // shortlist is empty, and returning "search failed" without making a single request turns a
  // degraded engine into a silent outage; the server's own default routing is still worth one
  // bounded call.
  if (!plans.length) plans.push({ tool, args: buildArgs(null) });

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
    error: `${attempts.join("; ") || "Fathom 搜索失败"}${openEngines.length ? `（服务端 open 引擎：${openEngines.join(", ")}）` : ""}`,
    sources: [],
    duration_ms: Date.now() - startedAt,
  };
}
