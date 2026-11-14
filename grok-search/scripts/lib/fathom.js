/**
 * fathom extra search channel.
 *
 * fathom is an MCP server that fans one query out across several web engines (brave,
 * google, bing, duckduckgo, baidu, ...). It is configured in config.json as
 * `fathomApiUrl` + `fathomApiKey` + `fathomSearchTool`; the tool name defaults to
 * `mega_search` but `search` (one engine) is the more reliable variant here.
 *
 * Engine health is not constant: `list_engines` reports a per-engine circuit breaker. Measured
 * against the live server: a `closed` engine answers, an `open` one fails at once with
 * `circuit_open` (or blocks for 13s and then answers `rate_limited`), and a `half-open` one was
 * still timing out at the budget a closed engine answers in. The adapter therefore plans only
 * `closed` engines and falls back to the server's own default routing when none is left.
 *
 * A failure of that fallback is an upstream engine failure, not a dead relay: the server
 * answered, and the same endpoint served a query minutes later. It therefore gets a short
 * cooldown instead of the full one, and any success clears it.
 */
import { mkdir, readFile, rename, unlink, writeFile } from "node:fs/promises";
import path from "node:path";
import { clearChannelCooldown, recordChannelCooldown } from "./cooldown.js";
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
 * Cooldown after a total engine failure.
 *
 * The relay is healthy in this case — it answered, and its upstream engines were rate limited or
 * breaker-open. A full 15-minute channel cooldown would disable a channel that served a query
 * four minutes later; no cooldown at all makes every command in the window pay the same ~16s for
 * the same answer. Three minutes is longer than the engine cache's own TTL, so the next attempt
 * after it re-probes instead of trusting the table that produced the failure.
 */
const ENGINE_FAILURE_COOLDOWN_MS = 3 * 60 * 1000;

/**
 * Whether the server blamed its upstream engines rather than failing as a relay.
 *
 * Both MCP error shapes put the server's body in the message, and a total engine failure always
 * names it: `all_engines_failed` with a per-engine `meta.engine_errors` list.
 */
function engineLevelFailure(error) {
  const text = String(error?.message || "");
  return text.includes("all_engines_failed") || text.includes("engine_errors");
}

/**
 * The engines the server reports as usable, or null when the probe failed. Open and closed
 * names are both kept: the closed ones become the plan, the open ones explain a total failure.
 */
function splitEngines(list) {
  const closed = [];
  const open = [];
  for (const engine of list) {
    const name = String(engine?.name || "").trim();
    if (!name) continue;
    (engine?.circuit_state === "closed" ? closed : open).push(name);
  }
  return { closed, open };
}

const ENGINES_CACHE_FILE = "fathom-engines.json";
// Engine health rotates slowly, so the probe is worth a short cache: a warm search should not
// pay an extra round trip, and the server's own view is what the plan is built from anyway.
const ENGINES_CACHE_TTL_MS = 120_000;
// A stale table is still far better than no table. The live relay failed `list_engines` while a
// two-minute-old cache said only yandex was closed; without this fallback the call fell back to
// the eight-engine ladder and burned 28.5s of its 30s budget, where the cached single engine
// answered in 4.9s. Beyond half an hour the table is a guess, so the ladder takes over again.
const ENGINES_STALE_MAX_MS = 30 * 60 * 1000;

/** The cached engine table for this endpoint, or null when missing, too old or from another URL. */
async function readEnginesCache(config, url, { maxAgeMs = ENGINES_CACHE_TTL_MS } = {}) {
  if (!config?.stateDir) return null;
  const file = path.join(config.stateDir, ENGINES_CACHE_FILE);
  let parsed;
  try {
    parsed = JSON.parse(await readFile(file, "utf8"));
  } catch (error) {
    if (error.code !== "ENOENT") debugLog(config, `fathom engine cache read skipped: ${error.message}`);
    return null;
  }
  // A changed endpoint is a different server; its engine table must not be reused.
  if (parsed?.auth_mode !== url) return null;
  const at = Date.parse(parsed?.at);
  if (!Number.isFinite(at) || Date.now() - at >= maxAgeMs) return null;
  const list = Array.isArray(parsed?.engines) ? parsed.engines : null;
  if (!list) return null;
  return { ...splitEngines(list), engines: list };
}

/** Cache only what the plan needs: engine names and breaker states, never the token. */
async function writeEnginesCache(config, url, probe) {
  if (!config?.stateDir) return;
  const file = path.join(config.stateDir, ENGINES_CACHE_FILE);
  const tmp = `${file}.${process.pid}.tmp`;
  const engines = probe.engines.map((engine) => ({ name: engine.name, circuit_state: engine.circuit_state }));
  try {
    await mkdir(config.stateDir, { recursive: true, mode: 0o700 });
    await writeFile(tmp, JSON.stringify({ auth_mode: url, at: new Date().toISOString(), engines }, null, 2), {
      encoding: "utf8",
      mode: 0o600,
    });
    await rename(tmp, file);
  } catch (error) {
    // A failed cache write only costs the next probe; it must not fail the search.
    await unlink(tmp).catch(() => {});
    debugLog(config, `fathom engine cache write skipped: ${error.message}`);
  }
}

async function probeEngines(url, token, config, startedAt) {
  const budgetLeft = fathomBudgetMs(config) - (Date.now() - startedAt);
  const timeoutMs = Math.max(200, Math.min(ENGINES_PROBE_TIMEOUT_MS, budgetLeft));
  try {
    const payload = await mcpSearch(url, token, "list_engines", {}, { timeoutMs, config });
    const list = Array.isArray(payload?.engines) ? payload.engines : null;
    if (!list) return null;
    return { ...splitEngines(list), engines: list };
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
 * The plans for one search, in the order they are tried.
 *
 * `mega_search` refuses a single-catalog engine outright ("engine \"arxiv\" is a single-catalog
 * engine and not allowed in mega tools"), so with that tool a configured name outside the web set
 * can never be planned. A single-engine tool has no such rule, so its configured names are kept.
 *
 * With a probe, only engines whose breaker is `closed` are planned: an `open` one fails
 * immediately with `circuit_open`, and a `half-open` one was still timing out at the budget a
 * closed engine answers in, so neither is worth a plan while a closed engine exists. Without a
 * probe the legacy order stands (fan-out, configured engines, then the web set).
 */
export function enginePlans({ engines = [], probe = null, tool = "mega_search", buildArgs = () => ({}) } = {}) {
  const configured = tool === "mega_search" ? engines.filter((engine) => WEB_ENGINES.includes(engine)) : engines;
  const plans = [];

  if (!probe) {
    // The fan-out still has to stay inside the web set: a mega call naming a catalog engine is
    // refused before any web engine runs, so one configured `arxiv` would burn the first plan.
    const legacyFanOut = configured.filter((engine) => WEB_ENGINES.includes(engine));
    if (legacyFanOut.length) plans.push({ tool, args: buildArgs(legacyFanOut.join(",")) });
    for (const engine of configured) plans.push({ tool, args: buildArgs(engine) });
    for (const engine of WEB_ENGINES) {
      if (!configured.includes(engine)) plans.push({ tool, args: buildArgs(engine) });
    }
    return plans;
  }

  // Candidate order: configured engines first, then the web engines in preference order.
  const healthy = new Set(probe.closed);
  const candidates = [];
  for (const engine of [...configured, ...WEB_ENGINES]) {
    if (healthy.has(engine) && !candidates.includes(engine)) candidates.push(engine);
  }
  const shortlist = candidates.slice(0, MAX_ENGINE_PLANS);
  for (const engine of shortlist) plans.push({ tool, args: buildArgs(engine) });
  // The fan-out waits for the slowest engine in the list, so it only runs after every
  // single-engine plan failed. One engine is not a fan-out.
  if (shortlist.length > 1) plans.push({ tool, args: buildArgs(shortlist.join(",")) });
  return plans;
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
  let probe = await readEnginesCache(config, url);
  if (!probe) {
    probe = await probeEngines(url, token, config, startedAt);
    if (probe) await writeEnginesCache(config, url, probe);
    // The probe can fail while its own last answer is still on disk (observed on the live relay:
    // a 136-second-old table said yandex was the only closed engine). Re-planning from that table
    // beats the ladder, which spent 28.5s of a 30s budget where the cached engine answered in 4.9s.
    else probe = await readEnginesCache(config, url, { maxAgeMs: ENGINES_STALE_MAX_MS });
  }
  const openEngines = probe ? probe.open : [];

  const plans = enginePlans({ engines, probe, tool, buildArgs });
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
      // A working call proves the relay is healthy again; a cooldown from an earlier failure must
      // not keep skipping it.
      await clearChannelCooldown(config, "fathom", url);
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

  // Every plan failed. A 5xx or a timeout means the relay is unhealthy, so a cooldown keeps
  // later commands from paying for the same failure — but a 502 that names the server's own
  // engine errors (`all_engines_failed`) is not relay death: the endpoint answered, and the
  // engines rotate. That case gets a short cooldown instead of the full one.
  if (lastError) {
    const engineLevel = engineLevelFailure(lastError);
    const relayLevel =
      lastError.timedOut || lastError.status === 401 || lastError.status === 403 || lastError.status >= 500;
    if (engineLevel || relayLevel) {
      await recordChannelCooldown(config, "fathom", {
        authMode: url,
        ...(engineLevel ? { retryAfterMs: ENGINE_FAILURE_COOLDOWN_MS } : {}),
        reason: engineLevel ? "all_engines_failed" : lastError.status ? `http_${lastError.status}` : "timeout",
      });
    }
  }

  return {
    ok: false,
    provider: "fathom",
    error: `${attempts.join("; ") || "Fathom 搜索失败"}${openEngines.length ? `（服务端 open 引擎：${openEngines.join(", ")}）` : ""}`,
    sources: [],
    duration_ms: Date.now() - startedAt,
  };
}
