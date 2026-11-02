/** Command-line surface for search.js: the usage text and argv parsing. */
import { normalizeSearchSource } from "./config.js";

const DEFAULT_MAX_CHARS = 30000;

export function usage() {
  return `Usage: ./scripts/search.js [--source web|x|both] [--instructions TEXT] [--platform NAME] [--model MODEL] [--extra N|--no-extra] [--source-chars N] [--max-sources N] [--full-sources] [--max-chars N] [--deadline SECONDS] <query>

Run a Responses-compatible Grok/OpenRouter search; every configured extra channel (Tavily/Firecrawl/Exa) searches the full --extra target and the union is deduped.

Cost:
  --responses-parallel-tool-calls false
                       Ask Grok for one server-side tool call per turn. Cuts X search calls
                       several-fold on relays that honor it; check diagnostics.responses_tool_calls.

Research instructions:
  --instructions TEXT  What Grok should return (fields, language, what to leave out). Only
                       Grok sees it; Tavily/Firecrawl/Exa still search the plain query.

Search sources:
  --source web         Grok web_search only (default)
  --source x           Grok x_search only; search X posts, profiles, and threads
  --source both        Grok decides between web_search and x_search
  --x-from-date DATE   Restrict X posts to on/after DATE (YYYY-MM-DD); implies X search
  --x-to-date DATE     Restrict X posts to on/before DATE (YYYY-MM-DD); implies X search
  --x-images           Analyze images in X posts; billed as extra tokens
  --x-videos           Analyze videos in X posts; billed as extra tokens
  --no-x-images        Turn off image analysis enabled in config
  --no-x-videos        Turn off video analysis enabled in config

Environment:
  GROK_API_URL         Responses-compatible base URL; required
  GROK_API_KEY         API key for GROK_API_URL; required
  GROK_API_PROVIDER    Optional provider: xai, openrouter, or openai-compatible
  GROK_MODEL           Optional default model; default grok-4.20-multi-agent-0309
  GROK_SEARCH_SOURCE   Optional default search source: web, x, or both; default web
  GROK_RESPONSES_MAX_TURNS
                       Optional Responses max_turns; default 3
  GROK_RESPONSES_PARALLEL_TOOL_CALLS
                       Optional true|false; false makes Grok search one call per turn. Not sent unless set
  GROK_DEFAULT_EXTRA   Optional per-channel Tavily/Firecrawl/Exa source count; default 6
  GROK_SOURCE_CHARS    Optional source snippet size; default 400
  GROK_MAX_SOURCES     Optional cap on returned source cards; default 12
  GROK_DEADLINE_SECONDS
                       Optional whole-command deadline; default 240, 0 disables
  TAVILY_API_KEY       Optional Tavily parallel source provider
  FIRECRAWL_API_KEY    Optional Firecrawl key; keyless search works without it
  GROK_OUTPUT_DIR      Optional directory for full answer when preview is truncated
`;
}

function parseIntOption(name, value, { min = 0 } = {}) {
  if (value == null || value === "") throw new Error(`${name} 缺少数值`);
  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed) || parsed < min) throw new Error(`${name} 必须是 >= ${min} 的整数`);
  return parsed;
}

function parseListOption(value) {
  return String(value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function parseListArg(name, value) {
  if (value == null || value === "") throw new Error(`${name} 缺少值`);
  return parseListOption(value);
}

function parseDateOption(name, value) {
  const date = String(value || "").trim();
  if (!date) throw new Error(`${name} 缺少值`);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) throw new Error(`${name} 必须是 ISO8601 日期（YYYY-MM-DD）`);
  // Date.parse rolls overflowing days over (2026-02-30 becomes Mar 2) instead of failing,
  // so compare the round-trip rather than just checking for NaN.
  const timestamp = Date.parse(`${date}T00:00:00Z`);
  if (Number.isNaN(timestamp) || new Date(timestamp).toISOString().slice(0, 10) !== date) {
    throw new Error(`${name} 不是有效日期: ${date}`);
  }
  return date;
}

export function parseArgs(argv) {
  const args = [...argv];
  const queryParts = [];
  let platform = "";
  let model = "";
  let extra = null;
  let extraMode = "auto";
  let extraSeen = false;
  let noExtraSeen = false;
  let sourceChars = null;
  let maxSources = null;
  let fullSources = false;
  let maxChars = DEFAULT_MAX_CHARS;
  let deadline = null;
  let responsesMaxTurns = null;
  let responsesReasoningEffort = "";
  let responsesParallelToolCalls = null;
  let responsesAllowedDomains = null;
  let responsesExcludedDomains = null;
  let searchSource = "";
  let responsesAllowedXHandles = null;
  let responsesExcludedXHandles = null;
  let xFromDate = "";
  let xToDate = "";
  let xImageUnderstanding = null;
  let xVideoUnderstanding = null;
  let responsesOpenRouterEngine = "";
  let instructions = "";

  while (args.length) {
    const arg = args.shift();
    if (arg === "--help" || arg === "-h") return { help: true };
    if (arg === "--instructions") {
      instructions = (args.shift() || "").trim();
      if (!instructions) throw new Error("--instructions 缺少值");
      continue;
    }
    if (arg?.startsWith("--instructions=")) {
      instructions = arg.slice("--instructions=".length).trim();
      if (!instructions) throw new Error("--instructions 缺少值");
      continue;
    }
    if (arg === "--platform") {
      platform = args.shift() || "";
      if (!platform) throw new Error("--platform 缺少值");
      continue;
    }
    if (arg?.startsWith("--platform=")) {
      platform = arg.slice("--platform=".length);
      continue;
    }
    if (arg === "--model") {
      model = args.shift() || "";
      if (!model) throw new Error("--model 缺少值");
      continue;
    }
    if (arg?.startsWith("--model=")) {
      model = arg.slice("--model=".length);
      continue;
    }
    if (arg === "--responses-max-turns") {
      responsesMaxTurns = parseIntOption("--responses-max-turns", args.shift(), { min: 1 });
      continue;
    }
    if (arg?.startsWith("--responses-max-turns=")) {
      responsesMaxTurns = parseIntOption("--responses-max-turns", arg.slice("--responses-max-turns=".length), { min: 1 });
      continue;
    }
    if (arg === "--responses-parallel-tool-calls" || arg?.startsWith("--responses-parallel-tool-calls=")) {
      const raw = arg.includes("=") ? arg.slice(arg.indexOf("=") + 1) : args.shift();
      if (!/^(true|false)$/i.test(String(raw || ""))) throw new Error("--responses-parallel-tool-calls 只能是 true 或 false");
      responsesParallelToolCalls = /^true$/i.test(raw);
      continue;
    }
    if (arg === "--responses-reasoning-effort") {
      responsesReasoningEffort = args.shift() || "";
      if (!responsesReasoningEffort) throw new Error("--responses-reasoning-effort 缺少值");
      continue;
    }
    if (arg?.startsWith("--responses-reasoning-effort=")) {
      responsesReasoningEffort = arg.slice("--responses-reasoning-effort=".length);
      continue;
    }
    if (arg === "--responses-allowed-domains") {
      responsesAllowedDomains = parseListArg("--responses-allowed-domains", args.shift());
      continue;
    }
    if (arg?.startsWith("--responses-allowed-domains=")) {
      responsesAllowedDomains = parseListOption(arg.slice("--responses-allowed-domains=".length));
      continue;
    }
    if (arg === "--responses-excluded-domains") {
      responsesExcludedDomains = parseListArg("--responses-excluded-domains", args.shift());
      continue;
    }
    if (arg?.startsWith("--responses-excluded-domains=")) {
      responsesExcludedDomains = parseListOption(arg.slice("--responses-excluded-domains=".length));
      continue;
    }
    if (arg === "--source") {
      searchSource = args.shift() || "";
      if (!searchSource) throw new Error("--source 缺少值");
      continue;
    }
    if (arg?.startsWith("--source=")) {
      searchSource = arg.slice("--source=".length);
      if (!searchSource) throw new Error("--source 缺少值");
      continue;
    }
    // Aliases kept from before --source existed; both mean the "both" mode.
    if (arg === "--responses-x-search" || arg === "--responses-include-x-search") {
      searchSource = "both";
      continue;
    }
    if (arg === "--x-from-date") {
      xFromDate = parseDateOption("--x-from-date", args.shift());
      continue;
    }
    if (arg?.startsWith("--x-from-date=")) {
      xFromDate = parseDateOption("--x-from-date", arg.slice("--x-from-date=".length));
      continue;
    }
    if (arg === "--x-to-date") {
      xToDate = parseDateOption("--x-to-date", args.shift());
      continue;
    }
    if (arg?.startsWith("--x-to-date=")) {
      xToDate = parseDateOption("--x-to-date", arg.slice("--x-to-date=".length));
      continue;
    }
    if (arg === "--x-images") {
      xImageUnderstanding = true;
      continue;
    }
    if (arg === "--no-x-images") {
      xImageUnderstanding = false;
      continue;
    }
    if (arg === "--x-videos") {
      xVideoUnderstanding = true;
      continue;
    }
    if (arg === "--no-x-videos") {
      xVideoUnderstanding = false;
      continue;
    }
    if (arg === "--responses-allowed-x-handles") {
      responsesAllowedXHandles = parseListArg("--responses-allowed-x-handles", args.shift());
      continue;
    }
    if (arg?.startsWith("--responses-allowed-x-handles=")) {
      responsesAllowedXHandles = parseListOption(arg.slice("--responses-allowed-x-handles=".length));
      continue;
    }
    if (arg === "--responses-excluded-x-handles") {
      responsesExcludedXHandles = parseListArg("--responses-excluded-x-handles", args.shift());
      continue;
    }
    if (arg?.startsWith("--responses-excluded-x-handles=")) {
      responsesExcludedXHandles = parseListOption(arg.slice("--responses-excluded-x-handles=".length));
      continue;
    }
    if (arg === "--responses-openrouter-engine") {
      responsesOpenRouterEngine = args.shift() || "";
      if (!responsesOpenRouterEngine) throw new Error("--responses-openrouter-engine 缺少值");
      continue;
    }
    if (arg?.startsWith("--responses-openrouter-engine=")) {
      responsesOpenRouterEngine = arg.slice("--responses-openrouter-engine=".length);
      continue;
    }
    if (arg === "--extra") {
      if (noExtraSeen) throw new Error("--extra 与 --no-extra 不能同时使用");
      extraSeen = true;
      extra = parseIntOption("--extra", args.shift(), { min: 0 });
      extraMode = extra > 0 ? "explicit" : "off";
      continue;
    }
    if (arg?.startsWith("--extra=")) {
      if (noExtraSeen) throw new Error("--extra 与 --no-extra 不能同时使用");
      extraSeen = true;
      extra = parseIntOption("--extra", arg.slice("--extra=".length), { min: 0 });
      extraMode = extra > 0 ? "explicit" : "off";
      continue;
    }
    if (arg === "--no-extra") {
      if (extraSeen) throw new Error("--extra 与 --no-extra 不能同时使用");
      noExtraSeen = true;
      extra = 0;
      extraMode = "off";
      continue;
    }
    if (arg === "--source-chars") {
      sourceChars = parseIntOption("--source-chars", args.shift(), { min: 0 });
      continue;
    }
    if (arg?.startsWith("--source-chars=")) {
      sourceChars = parseIntOption("--source-chars", arg.slice("--source-chars=".length), { min: 0 });
      continue;
    }
    if (arg === "--max-sources") {
      maxSources = parseIntOption("--max-sources", args.shift(), { min: 1 });
      continue;
    }
    if (arg?.startsWith("--max-sources=")) {
      maxSources = parseIntOption("--max-sources", arg.slice("--max-sources=".length), { min: 1 });
      continue;
    }
    if (arg === "--deadline") {
      deadline = parseIntOption("--deadline", args.shift(), { min: 0 });
      continue;
    }
    if (arg?.startsWith("--deadline=")) {
      deadline = parseIntOption("--deadline", arg.slice("--deadline=".length), { min: 0 });
      continue;
    }
    if (arg === "--full-sources") {
      fullSources = true;
      continue;
    }
    if (arg === "--max-chars") {
      maxChars = parseIntOption("--max-chars", args.shift(), { min: 0 });
      continue;
    }
    if (arg?.startsWith("--max-chars=")) {
      maxChars = parseIntOption("--max-chars", arg.slice("--max-chars=".length), { min: 0 });
      continue;
    }
    if (arg?.startsWith("-")) throw new Error(`未知参数: ${arg}`);
    queryParts.push(arg);
  }

  const query = queryParts.join(" ").trim();
  if (!query) throw new Error("缺少 query");
  if (xFromDate && xToDate && xFromDate > xToDate) throw new Error("--x-from-date 不能晚于 --x-to-date");
  // Reject an unknown source here so it fails like every other argument error, instead of
  // after config load and output-dir cleanup.
  if (searchSource) normalizeSearchSource(searchSource);

  return {
    query,
    platform,
    model,
    extra,
    extraMode,
    sourceChars,
    maxSources,
    fullSources,
    maxChars,
    deadline,
    responsesMaxTurns,
    responsesReasoningEffort,
    responsesParallelToolCalls,
    responsesAllowedDomains,
    responsesExcludedDomains,
    searchSource,
    responsesAllowedXHandles,
    responsesExcludedXHandles,
    xFromDate,
    xToDate,
    xImageUnderstanding,
    xVideoUnderstanding,
    responsesOpenRouterEngine,
    instructions,
  };
}
