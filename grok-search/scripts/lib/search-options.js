/** Search option resolution from CLI args over config, plus the diagnostics derived from them. */
import {
  ConfigError,
  normalizeOpenRouterSearchEngine,
  normalizeSearchSource,
  usesWebSearch,
  usesXSearch,
  X_HANDLE_LIMIT,
} from "./config.js";
import { SEARCH_BUDGET_TOTAL, SEARCH_BUDGET_X } from "./prompts.js";
import { resolveFilterPair, validateExclusiveLists, validateMaxItems } from "./search-filters.js";

/**
 * Only command-line X options imply X search. Configured handle lists and media flags
 * are standing preferences for when X search runs; letting them switch the source on
 * would turn a configured restriction into a billed extra search channel.
 */
function xOptionsRequested(args) {
  return Boolean(
    args.responsesAllowedXHandles?.length ||
      args.responsesExcludedXHandles?.length ||
      args.xFromDate ||
      args.xToDate ||
      args.xImageUnderstanding ||
      args.xVideoUnderstanding
  );
}

function resolveSearchSource(args, config) {
  const requested = args.searchSource || config.responsesSearchSource;
  const source = normalizeSearchSource(requested || "web");
  const explicit = Boolean(requested);
  if (!xOptionsRequested(args) || usesXSearch(source)) return { source, explicit };
  // X-specific filters are meaningless without X search: promote a defaulted source,
  // but never silently override an explicit --source web.
  if (args.searchSource) {
    throw new ConfigError("--source web 与 X 过滤参数（handles / dates / media）冲突", "SEARCH_SOURCE_CONFLICT");
  }
  return { source: "both", explicit };
}

export function resolveSearchOptions(args, config) {
  const domainFilters = resolveFilterPair({
    argsAllowed: args.responsesAllowedDomains,
    argsExcluded: args.responsesExcludedDomains,
    configAllowed: config.responsesAllowedDomains,
    configExcluded: config.responsesExcludedDomains,
    allowedName: "responses allowed domains",
    excludedName: "responses excluded domains",
    max: 5,
  });
  const xHandleFilters = resolveFilterPair({
    argsAllowed: args.responsesAllowedXHandles,
    argsExcluded: args.responsesExcludedXHandles,
    configAllowed: config.responsesAllowedXHandles,
    configExcluded: config.responsesExcludedXHandles,
    allowedName: "responses allowed X handles",
    excludedName: "responses excluded X handles",
    max: X_HANDLE_LIMIT,
  });
  const allowedDomains = domainFilters.allowed;
  const excludedDomains = domainFilters.excluded;
  const allowedXHandles = xHandleFilters.allowed;
  const excludedXHandles = xHandleFilters.excluded;

  validateExclusiveLists(allowedDomains, excludedDomains, "responses allowed domains", "responses excluded domains");
  validateExclusiveLists(allowedXHandles, excludedXHandles, "responses allowed X handles", "responses excluded X handles");
  validateMaxItems(allowedDomains, "responses allowed domains", 5);
  validateMaxItems(excludedDomains, "responses excluded domains", 5);
  validateMaxItems(allowedXHandles, "responses allowed X handles", X_HANDLE_LIMIT);
  validateMaxItems(excludedXHandles, "responses excluded X handles", X_HANDLE_LIMIT);

  const source = resolveSearchSource(args, config);

  return {
    model: args.model || config.grokModel,
    maxTurns: args.responsesMaxTurns ?? config.responsesMaxTurns,
    reasoningEffort: args.responsesReasoningEffort || config.responsesReasoningEffort,
    parallelToolCalls: args.responsesParallelToolCalls ?? config.responsesParallelToolCalls ?? null,
    allowedDomains,
    excludedDomains,
    searchSource: source.source,
    explicitSearchSource: source.explicit,
    allowedXHandles,
    excludedXHandles,
    xFromDate: args.xFromDate,
    xToDate: args.xToDate,
    xImageUnderstanding: args.xImageUnderstanding ?? config.responsesXImageUnderstanding,
    xVideoUnderstanding: args.xVideoUnderstanding ?? config.responsesXVideoUnderstanding,
    openRouterEngine: normalizeOpenRouterSearchEngine(args.responsesOpenRouterEngine || config.responsesOpenRouterEngine),
    instructions: args.instructions || "",
    days: args.days ?? null,
  };
}

/**
 * OpenRouter attaches x_search to native web search for xAI models with no way to turn
 * either side off, so the requested source is only a hint there. Say so rather than
 * letting the diagnostics claim a mode that was not enforced.
 */
export function searchSourceWarnings(searchOptions, config) {
  const warnings = [];
  if (config.apiProvider !== "openrouter") return warnings;

  const { searchSource, openRouterEngine } = searchOptions;
  const nativeCapable = openRouterEngine === "auto" || openRouterEngine === "native";

  if (!usesXSearch(searchSource)) {
    // Only worth saying when the caller actually asked for web-only; on the default path
    // it is unactionable noise on every single OpenRouter search.
    if (nativeCapable && searchOptions.explicitSearchSource) {
      warnings.push("OpenRouter may attach x_search to native web search for xAI models; --source web is not enforced there.");
    }
    return warnings;
  }

  if (!usesWebSearch(searchSource)) {
    warnings.push("OpenRouter cannot run x_search alone; web search stays enabled alongside it.");
  }
  if (!nativeCapable) {
    warnings.push(`OpenRouter engine "${openRouterEngine}" replaces native search, so x_search and its filters do not run.`);
  }
  return warnings;
}

export function responsesDiagnosticOptions(searchOptions) {
  return {
    responses_max_turns: searchOptions.maxTurns,
    responses_reasoning_effort: searchOptions.reasoningEffort,
    ...(typeof searchOptions.parallelToolCalls === "boolean" ? { responses_parallel_tool_calls: searchOptions.parallelToolCalls } : {}),
    responses_allowed_domains: searchOptions.allowedDomains,
    responses_excluded_domains: searchOptions.excludedDomains,
    search_source: searchOptions.searchSource,
    ...(usesXSearch(searchOptions.searchSource)
      ? {
          responses_allowed_x_handles: searchOptions.allowedXHandles,
          responses_excluded_x_handles: searchOptions.excludedXHandles,
          ...(searchOptions.xFromDate ? { x_from_date: searchOptions.xFromDate } : {}),
          ...(searchOptions.xToDate ? { x_to_date: searchOptions.xToDate } : {}),
          ...(searchOptions.xImageUnderstanding ? { x_image_understanding: true } : {}),
          ...(searchOptions.xVideoUnderstanding ? { x_video_understanding: true } : {}),
        }
      : {}),
    responses_openrouter_engine: searchOptions.openRouterEngine,
    ...(searchOptions.instructions ? { instructions_chars: searchOptions.instructions.length } : {}),
    ...(searchOptions.days != null ? { days: searchOptions.days } : {}),
  };
}

/**
 * The prompts ask for about SEARCH_BUDGET_TOTAL searches (SEARCH_BUDGET_X of them on X).
 * That is advice, not a cap: max_turns bounds agentic turns and a turn can hold several
 * calls, so `enforced` stays false until a provider-side limit is wired in.
 */
export function searchBudget(searchSource, diagnostics) {
  const usedWeb = diagnostics.responses_web_search_calls ?? 0;
  const usedX = diagnostics.responses_x_search_calls ?? 0;
  const promptX = usesXSearch(searchSource) ? SEARCH_BUDGET_X : 0;
  return {
    prompt_total: SEARCH_BUDGET_TOTAL,
    prompt_x: promptX,
    used_web: usedWeb,
    used_x: usedX,
    used_total: usedWeb + usedX,
    exceeded: usedWeb + usedX > SEARCH_BUDGET_TOTAL || usedX > promptX,
    enforced: false,
  };
}
