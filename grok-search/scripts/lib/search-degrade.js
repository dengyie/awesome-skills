/** Degraded-search machinery: failure labels, the raw-extras fallback answer, and failure diagnostics. */
import { firecrawlAuthMode } from "./firecrawl.js";
import { responsesDiagnosticOptions } from "./search-options.js";

export const GROK_FAILURE_LABELS = {
  quota: { code: "QUOTA_EXHAUSTED", errorCode: "GROK_QUOTA_EXHAUSTED", label: "额度已耗尽", warning: "Grok Responses quota was exhausted." },
  rate_limit: { code: "RATE_LIMITED", errorCode: "GROK_RATE_LIMITED", label: "触发限流", warning: "Grok Responses was rate limited." },
  no_search: { code: "NO_SEARCH", errorCode: "GROK_RESPONSES_NO_SEARCH", label: "未执行服务端搜索", warning: "Grok Responses returned an answer without server-side web_search." },
  empty: { code: "EMPTY", errorCode: "GROK_RESPONSES_EMPTY", label: "返回空内容", warning: "Grok Responses returned empty content." },
  timeout: { code: "TIMEOUT", errorCode: "GROK_TIMEOUT", label: "请求超时", warning: "Grok Responses timed out." },
  upstream: { code: "UPSTREAM", errorCode: "GROK_UPSTREAM", label: "上游不可用", warning: "Grok Responses upstream failed." },
};

export function grokFailureAttempt(config, error) {
  return { provider: `grok-responses:${config.apiProvider}`, ok: false, count: 0, error: error.message };
}

export function clipText(value, max = 800) {
  const text = String(value || "").trim();
  if (!text) return "";
  return text.length > max ? `${text.slice(0, max).trimEnd()}…` : text;
}

export function degradedAnswer(sources, label) {
  const lines = [
    `> ⚠️ Grok Responses ${label}。以下为 Tavily / Firecrawl / Exa 原始搜索结果，未经 Grok 综合生成。`,
    "",
  ];
  const groups = new Map();
  for (const source of sources) {
    const provider = source.provider || "search";
    if (!groups.has(provider)) groups.set(provider, []);
    groups.get(provider).push(source);
  }
  for (const [provider, items] of groups) {
    lines.push(`## ${provider === "tavily" ? "Tavily" : provider === "firecrawl" ? "Firecrawl" : provider === "exa" ? "Exa" : provider}`);
    lines.push("");
    for (const [index, source] of items.entries()) {
      const title = String(source.title || `Result ${index + 1}`).trim();
      lines.push(`${index + 1}. [${title}](${source.url})`);
      const snippet = clipText(source.snippet || source.description || source.content);
      if (snippet) lines.push(`   ${snippet.replace(/\s+/g, " ")}`);
    }
    lines.push("");
  }
  return lines.join("\n").trim();
}

export function failureDiagnostics(config, searchOptions, extraOptions, extra, error, { failure = null } = {}) {
  const labels = failure ? GROK_FAILURE_LABELS[failure] : null;
  const warning = labels ? labels.warning : `Responses search failed: ${error.message}`;
  return {
    grok_endpoint: "responses",
    ...(labels ? { grok_error: { code: labels.code, message: error.message } } : {}),
    warnings: [warning, ...(extra?.warnings || []), ...(error?.diagnostics?.warnings || [])],
    ...(error?.diagnostics?.responses_native_search === false ? { responses_native_search: false } : {}),
    ...(Number.isFinite(error?.diagnostics?.responses_web_search_calls)
      ? { responses_web_search_calls: error.diagnostics.responses_web_search_calls }
      : {}),
    provider_attempts: [grokFailureAttempt(config, error), ...(extra?.provider_attempts || [])],
    options: {
      api_provider: config.apiProvider,
      extra: extraOptions.limit,
      extra_mode: extraOptions.mode,
      extra_allocation: extra?.allocation || { tavily: 0, firecrawl: 0, exa: 0 },
      firecrawl_auth_mode: extraOptions.limit > 0 ? firecrawlAuthMode(config) : null,
      ...responsesDiagnosticOptions(searchOptions),
    },
  };
}
