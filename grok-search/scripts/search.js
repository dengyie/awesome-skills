#!/usr/bin/env node
import { realpathSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { loadConfig } from "./lib/config.js";
import { startDeadline } from "./lib/deadline.js";
import {
  classifyGrokFailure,
  grokDegradeKind,
  grokRequestTimeoutMs,
  searchGrokResponses,
  summarizeToolCalls,
} from "./lib/grok-responses.js";
import { cleanupOutputDir, previewText, printJson, runRecordBase, writeRunRecord, writeRunRecordSync } from "./lib/output.js";
import { firecrawlAuthMode } from "./lib/firecrawl.js";
import { assertProxyUsable, getProxyState } from "./lib/proxy.js";
import { buildRawSourcesPayload, compactSources, mergeSources, selectSources } from "./lib/sources.js";
import { degradedAnswer, failureDiagnostics, GROK_FAILURE_LABELS, grokFailureAttempt } from "./lib/search-degrade.js";
import { extraModeWarnings, extraSources, resolveExtra } from "./lib/search-extras.js";
import { parseArgs, usage } from "./lib/search-argv.js";
import { responsesDiagnosticOptions, resolveSearchOptions, searchBudget, searchSourceWarnings } from "./lib/search-options.js";

async function grokChannel(args, config, searchOptions, { timeoutMs } = {}) {
  const grok = await searchGrokResponses(
    args.query,
    {
      platform: args.platform,
      model: searchOptions.model,
      maxTurns: searchOptions.maxTurns,
      reasoningEffort: searchOptions.reasoningEffort,
      parallelToolCalls: searchOptions.parallelToolCalls,
      allowedDomains: searchOptions.allowedDomains,
      excludedDomains: searchOptions.excludedDomains,
      searchSource: searchOptions.searchSource,
      allowedXHandles: searchOptions.allowedXHandles,
      excludedXHandles: searchOptions.excludedXHandles,
      xFromDate: searchOptions.xFromDate,
      xToDate: searchOptions.xToDate,
      xImageUnderstanding: searchOptions.xImageUnderstanding,
      xVideoUnderstanding: searchOptions.xVideoUnderstanding,
      openRouterEngine: searchOptions.openRouterEngine,
      instructions: searchOptions.instructions,
      timeoutMs,
    },
    config
  );
  const diagnostics = { ...(grok.diagnostics || {}) };
  const warnings = [...(diagnostics.warnings || [])];
  delete diagnostics.warnings;
  const toolCalls = Array.isArray(diagnostics.responses_tool_calls) ? diagnostics.responses_tool_calls : [];
  const toolCallTotal = diagnostics.responses_tool_call_total ?? toolCalls.length;
  const toolCallCounts = diagnostics.responses_tool_call_counts ?? null;
  delete diagnostics.responses_tool_call_total;
  delete diagnostics.responses_tool_call_counts;
  diagnostics.responses_tool_calls = summarizeToolCalls(toolCalls, toolCallTotal, toolCallCounts);
  diagnostics.search_budget = searchBudget(searchOptions.searchSource, diagnostics);
  if (!grok.sources.length) warnings.push("No responses citations or searched sources were found.");
  return {
    endpoint: grok.endpoint,
    model: grok.model,
    answer: grok.content,
    sources: grok.sources,
    tool_calls: toolCalls,
    warnings,
    provider_attempts: [{ provider: `grok-responses:${config.apiProvider}`, ok: true, count: grok.sources.length }],
    diagnostics,
    raw_content_chars: grok.content.length,
    raw: grok.raw,
  };
}

async function publicResult(args, config) {
  const startedAtMs = Date.now();
  const searchOptions = resolveSearchOptions(args, config);
  const sourceChars = args.sourceChars ?? config.sourceChars;
  const maxSources = args.maxSources ?? config.maxSources;
  const extraOptions = resolveExtra(args, config, searchOptions.searchSource);
  const deadlineSeconds = args.deadline ?? config.deadlineSeconds;
  const grokPromise = grokChannel(args, config, searchOptions, {
    timeoutMs: grokRequestTimeoutMs(deadlineSeconds),
  }).then(
    (value) => ({ ok: true, value }),
    (error) => ({ ok: false, error })
  );
  const [grokResult, extra] = await Promise.all([
    grokPromise,
    extraSources(args.query, extraOptions.limit, config, {
      allowedDomains: searchOptions.allowedDomains,
      excludedDomains: searchOptions.excludedDomains,
      days: searchOptions.days,
    }),
  ]);

  let grok;
  let degraded = false;
  let grokError = null;
  if (grokResult.ok) {
    grok = grokResult.value;
  } else {
    const extrasReady = extraOptions.limit > 0 && extra.sources.length > 0;
    const named = classifyGrokFailure(grokResult.error);
    // Quota and rate-limit are named even without extras. Timeouts, 5xx, and replies without
    // usable search still leave Tavily/Firecrawl/Exa results on the table; auth and protocol
    // errors (401/403/422 without a quota body) stay hard failures even when extras exist.
    const failure = extrasReady ? named || grokDegradeKind(grokResult.error) : named;
    if (!failure) {
      grokResult.error.diagnostics = failureDiagnostics(config, searchOptions, extraOptions, extra, grokResult.error);
      throw grokResult.error;
    }
    const labels = GROK_FAILURE_LABELS[failure];
    if (!extrasReady) {
      const error = new Error(
        extraOptions.mode === "off-x-only"
          ? `Grok Responses ${labels.label}；--source x 下 extra sources 默认关闭（传 --extra N 可开启），无法降级`
          : extraOptions.limit <= 0
            ? `Grok Responses ${labels.label}；extra sources 已显式关闭，无法降级`
            : `Grok Responses ${labels.label}，且 Tavily/Firecrawl/Exa 未返回可用结果`
      );
      error.code = labels.errorCode;
      error.diagnostics = failureDiagnostics(config, searchOptions, extraOptions, extra, grokResult.error, { failure });
      throw error;
    }
    degraded = true;
    grokError = { code: labels.code, message: grokResult.error.message };
    grok = {
      endpoint: "responses",
      model: searchOptions.model,
      answer: degradedAnswer(extra.sources, labels.label),
      sources: [],
      tool_calls: [],
      warnings: [
        `Grok Responses 因${labels.label}不可用；当前 answer 仅包含 Tavily/Firecrawl/Exa 原始搜索结果，未经 Grok 综合生成。`,
      ],
      provider_attempts: [grokFailureAttempt(config, grokResult.error)],
      diagnostics: {},
      raw_content_chars: 0,
    };
  }

  const warnings = [...searchSourceWarnings(searchOptions, config), ...extraModeWarnings(extraOptions), ...grok.warnings, ...extra.warnings];
  const providerAttempts = [...grok.provider_attempts, ...extra.provider_attempts];
  const rawGrokSources = grok.sources;
  const rawExtraSources = extra.sources;
  const rawMergedSources = mergeSources(rawGrokSources, rawExtraSources);
  const selected = selectSources(rawMergedSources, {
    maxSources,
    allowedDomains: searchOptions.allowedDomains,
    excludedDomains: searchOptions.excludedDomains,
  });
  const itemsCompact = compactSources(selected.items, { sourceChars });
  const mergedCompactFull = compactSources(rawMergedSources, { sourceChars });

  const answerInfo = await previewText(config, {
    kind: "search",
    provider: degraded ? "search-fallback" : "grok-responses",
    label: args.query,
    content: grok.answer,
    maxChars: args.maxChars,
    extension: "md",
  });
  const createdAt = new Date().toISOString();
  const rawPayload = buildRawSourcesPayload({
    query: args.query,
    grok: rawGrokSources,
    extra: rawExtraSources,
    providerRaw: extra.provider_raw,
    providerAttempts,
    grokToolCalls: grok.tool_calls,
    createdAt,
  });
  const diagnostics = {
    grok_endpoint: "responses",
    ...grok.diagnostics,
    ...(degraded ? { degraded: true, grok_error: grokError } : {}),
    warnings,
    provider_attempts: providerAttempts,
    options: {
      api_provider: config.apiProvider,
      extra: extraOptions.limit,
      extra_mode: extraOptions.mode,
      extra_allocation: extra.allocation,
      // Domain filters are pushed to Tavily/Firecrawl/Exa as well; results that still fall
      // outside them are ranked last (see sources.js selectSources).
      extra_domain_filter:
        extraOptions.limit > 0 && (searchOptions.allowedDomains.length || searchOptions.excludedDomains.length) ? "pushed" : "none",
      firecrawl_auth_mode: extraOptions.limit > 0 ? firecrawlAuthMode(config) : null,
      source_chars: sourceChars,
      max_sources: maxSources,
      max_chars: args.maxChars,
      full_sources: args.fullSources,
      ...(getProxyState().mode === "direct" ? {} : { proxy_mode: getProxyState().mode }),
      ...responsesDiagnosticOptions(searchOptions),
    },
    raw_grok_content_chars: grok.raw_content_chars,
    duration_ms: Date.now() - startedAtMs,
    searched_at: createdAt,
  };

  // The run record is the durable copy of this call: full answer, every source (not just the
  // 12 shown), provider raw payloads, tool calls, usage. stdout only carries its path.
  const runPath = await writeRunRecord(config, {
    kind: "search",
    label: args.query,
    record: {
      ...runRecordBase("search", config, createdAt),
      query: args.query,
      instructions: args.instructions || null,
      platform: args.platform || null,
      model: grok.model,
      options: diagnostics.options,
      answer: grok.answer,
      sources: {
        grok: rawGrokSources,
        extra: rawExtraSources,
        items: mergedCompactFull,
        returned: selected.returned,
        total: selected.total,
        omitted: selected.omitted,
      },
      provider_raw: rawPayload.provider_raw,
      provider_attempts: providerAttempts,
      grok_tool_calls: grok.tool_calls,
      diagnostics,
      error: null,
      ...(config.debugRaw || args.fullSources ? { grok_raw: grok.raw ?? null } : {}),
    },
  });
  const sources = {
    items: itemsCompact,
    returned: selected.returned,
    total: selected.total,
    omitted: selected.omitted,
    raw_path: runPath,
  };
  if (args.fullSources) sources.raw = rawPayload;

  return {
    query: args.query,
    platform: args.platform || null,
    model: grok.model,
    answer: {
      text: answerInfo.preview,
      chars: answerInfo.preview.length,
      original_chars: answerInfo.original_length,
      truncated: answerInfo.truncated,
      full_path: answerInfo.full_output_path,
    },
    sources,
    diagnostics,
  };
}

function errorOutput(error, code, diagnostics = {}) {
  return {
    error: { message: error.message, code },
    diagnostics: {
      warnings: [],
      provider_attempts: [],
      searched_at: new Date().toISOString(),
      ...diagnostics,
    },
  };
}

function errorRunRecord(config, args, output) {
  return {
    ...runRecordBase("search", config, output.diagnostics.searched_at),
    query: args?.query ?? null,
    error: output.error,
    diagnostics: output.diagnostics,
  };
}

function entryHref(argvPath) {
  const resolved = path.resolve(argvPath);
  try {
    return pathToFileURL(realpathSync(resolved)).href;
  } catch {
    return pathToFileURL(resolved).href;
  }
}

// Node resolves import.meta.url through the real path. argv[1] stays as invoked, so a
// symlink such as ~/.agents/skills/grok-search must be resolved before the comparison or
// the CLI exits 0 without running.
const isMain = Boolean(process.argv[1]) && import.meta.url === entryHref(process.argv[1]);

if (isMain) {
let stage = "argument";
let args = null;
let config = null;
try {
  args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
    process.exit(0);
  }
  stage = "config";
  config = await loadConfig({ requireGrok: true });
  assertProxyUsable();
  await cleanupOutputDir(config);
  stage = "search";
  const deadlineSeconds = args.deadline ?? config.deadlineSeconds;
  const stopDeadline = startDeadline(deadlineSeconds, () => {
    const error = new Error(`搜索总耗时超过 deadline（>${deadlineSeconds}s），已中止`);
    const output = errorOutput(error, "DEADLINE_EXCEEDED");
    const runPath = writeRunRecordSync(config, { kind: "search", label: args.query, record: errorRunRecord(config, args, output) });
    if (runPath) output.diagnostics.run_path = runPath;
    printJson(output);
    console.error(error.message);
    process.exit(1);
  });
  try {
    printJson(await publicResult(args, config));
  } finally {
    stopDeadline();
  }
} catch (error) {
  const code = error.code || (stage === "argument" ? "ARGUMENT_ERROR" : stage === "search" ? "SEARCH_ERROR" : "RUNTIME_ERROR");
  const output = errorOutput(error, code, error.diagnostics);
  if (config) {
    const runPath = await writeRunRecord(config, { kind: "search", label: args?.query || "error", record: errorRunRecord(config, args, output) });
    if (runPath) output.diagnostics.run_path = runPath;
  }
  printJson(output);
  console.error(error.message);
  process.exitCode = stage === "argument" ? 2 : 1;
}
}
