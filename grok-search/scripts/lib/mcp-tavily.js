/**
 * MCP-Tavily extra search channel.
 *
 * A Tavily-compatible MCP relay configured in config.json as `mcpTavilyUrl` +
 * `mcpTavilyToken` + `mcpTavilyTool` (default `search_proxy_tavily_search`). It answers
 * with the Tavily search payload — `results[]` with `url`, `title`, `content` and
 * `score` — wrapped in the MCP text envelope.
 */
import { clearChannelCooldown, recordChannelCooldown } from "./cooldown.js";
import { debugLog } from "./http.js";
import { hasMcpConfig, mcpSearch } from "./mcp.js";

const MCP_TAVILY_TIMEOUT_MS = 90_000;

export function hasMcpTavily(config) {
  return hasMcpConfig(config, { urlKey: "mcpTavilyUrl", tokenKey: "mcpTavilyToken" });
}

function toolName(config) {
  const tool = String(config?.mcpTavilyTool || "").trim();
  return tool || "search_proxy_tavily_search";
}

/** The relay returns Tavily's shape, so the row mapping matches tavily.js. */
function sourceFromMcpTavily(result) {
  const url = typeof result?.url === "string" ? result.url.trim() : "";
  if (!url) return null;
  const title = typeof result?.title === "string" ? result.title.trim() : "";
  const content = typeof result?.content === "string" ? result.content.trim() : "";
  const published = typeof result?.published_date === "string" ? result.published_date.trim() : "";
  return {
    url,
    provider: "mcpTavily",
    ...(title ? { title } : {}),
    ...(content ? { description: content } : {}),
    ...(published ? { published_date: published } : {}),
    ...(Number.isFinite(result?.score) ? { score: result.score } : {}),
  };
}

function results(payload) {
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.data)) return payload.data;
  return [];
}

export async function mcpTavilySearch(query, limit, config, filters = {}) {
  if (!hasMcpTavily(config)) {
    return { ok: false, provider: "mcpTavily", skipped: true, error: "MCP_TAVILY_TOKEN 未配置", sources: [] };
  }

  const url = String(config?.mcpTavilyUrl || "").trim();
  const token = String(config?.mcpTavilyToken || "").trim();
  const startedAt = Date.now();

  const allowed = Array.isArray(filters?.allowedDomains) ? filters.allowedDomains : [];
  const excluded = Array.isArray(filters?.excludedDomains) ? filters.excludedDomains : [];
  const days = Number.isFinite(filters?.days) && filters.days > 0 ? filters.days : null;

  const args = {
    query,
    max_results: Math.min(limit, 20),
    search_depth: "advanced",
    include_answer: false,
    include_raw_content: false,
    ...(days != null ? { days } : {}),
    ...(allowed.length ? { include_domains: allowed } : {}),
    ...(excluded.length ? { exclude_domains: excluded } : {}),
  };

  try {
    const payload = await mcpSearch(url, token, toolName(config), args, {
      timeoutMs: MCP_TAVILY_TIMEOUT_MS,
      config,
    });
    const rows = results(payload);
    // A working call proves the relay is healthy again; a cooldown from an earlier failure must
    // not keep skipping it until it expires.
    await clearChannelCooldown(config, "mcpTavily", url);
    return {
      ok: true,
      provider: "mcpTavily",
      sources: rows.map(sourceFromMcpTavily).filter(Boolean).slice(0, limit),
      raw: payload,
      duration_ms: Date.now() - startedAt,
    };
  } catch (error) {
    debugLog(config, `mcpTavily search failed: ${error.message}`);
    // An unhealthy relay would otherwise be re-billed on every command. A 5xx or a timeout
    // opens a short cooldown; a 401/403 (bad token) does too, since retrying it cannot work.
    if (error.status >= 500 || error.timedOut || error.status === 401 || error.status === 403) {
      await recordChannelCooldown(config, "mcpTavily", {
        authMode: url,
        reason: error.status ? `http_${error.status}` : "timeout",
      });
    }
    return {
      ok: false,
      provider: "mcpTavily",
      error: error.message,
      sources: [],
      duration_ms: Date.now() - startedAt,
    };
  }
}
