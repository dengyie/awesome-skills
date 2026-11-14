import { readFile } from "node:fs/promises";
import { homedir } from "node:os";
import path from "node:path";

export class ConfigError extends Error {
  constructor(message, code = "CONFIG_ERROR") {
    super(message);
    this.name = "ConfigError";
    this.code = code;
  }
}

const DEFAULT_MODEL = "grok-4.20-multi-agent-0309";
const DEFAULT_EXTRA = 6;
export const DEFAULT_SOURCE_CHARS = 400;
export const DEFAULT_MAX_SOURCES = 12;
const DEFAULT_DEADLINE_SECONDS = 240;
const DEFAULT_TAVILY_API_URL = "https://api.tavily.com";
const DEFAULT_FIRECRAWL_API_URL = "https://api.firecrawl.dev/v2";
const DEFAULT_EXA_API_URL = "https://api.exa.ai";
const DEFAULT_STATE_DIR = path.join(homedir(), ".cache", "grok-search");
const DEFAULT_OUTPUT_DIR = path.join(DEFAULT_STATE_DIR, "outputs");
const DEFAULT_OUTPUT_RETENTION_DAYS = 30;
const DEFAULT_RESPONSES_MAX_TURNS = 3;
const DEFAULT_RESPONSES_REASONING_EFFORT = "low";
const DEFAULT_RESPONSES_OPENROUTER_ENGINE = "auto";
const DEFAULT_SEARCH_SOURCE = "web";
const API_PROVIDERS = new Set(["xai", "openrouter", "openai-compatible"]);
const OPENROUTER_SEARCH_ENGINES = new Set(["auto", "native", "exa", "firecrawl", "parallel", "perplexity"]);
const SEARCH_SOURCES = new Set(["web", "x", "both"]);
export const X_HANDLE_LIMIT = 20;

function env(name) {
  const value = process.env[name];
  return value && value.trim() ? value.trim() : undefined;
}

function envBool(name, defaultValue = false) {
  const value = env(name);
  if (value == null) return defaultValue;
  return parseBoolValue(value, defaultValue);
}

function envInt(name, defaultValue, { min = Number.MIN_SAFE_INTEGER } = {}) {
  const value = env(name);
  if (value == null) return defaultValue;
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) && parsed >= min ? parsed : defaultValue;
}

function envFloat(name, defaultValue, { min = -Infinity } = {}) {
  const value = env(name);
  if (value == null) return defaultValue;
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) && parsed >= min ? parsed : defaultValue;
}

function parseConfigInt(value, fallback, { min = Number.MIN_SAFE_INTEGER } = {}) {
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) && parsed >= min ? parsed : fallback;
}

function parseBoolValue(value, fallback = false) {
  if (typeof value === "boolean") return value;
  if (typeof value === "number") return value !== 0;
  if (typeof value !== "string") return fallback;
  const normalized = value.trim().toLowerCase();
  if (["1", "true", "yes", "on"].includes(normalized)) return true;
  if (["0", "false", "no", "off"].includes(normalized)) return false;
  return fallback;
}

function parseListValue(value) {
  const items = Array.isArray(value) ? value : typeof value === "string" ? value.split(",") : [];
  return items.map((item) => String(item || "").trim()).filter(Boolean);
}

export function configFilePath() {
  return path.join(homedir(), ".config", "grok-search", "config.json");
}

/**
 * Decode a config file by its byte-order mark.
 *
 * Windows editors and shells write BOMs that JSON.parse rejects: PowerShell 5.1's
 * `Set-Content -Encoding utf8` emits UTF-8 with BOM, and `Out-File` emits UTF-16LE. Reading the
 * file as a Buffer and decoding here keeps a correctly-authored config working instead of
 * failing every command with "not valid JSON".
 */
function decodeConfigText(buffer) {
  if (buffer.length >= 3 && buffer[0] === 0xef && buffer[1] === 0xbb && buffer[2] === 0xbf) {
    return buffer.subarray(3).toString("utf8");
  }
  if (buffer.length >= 2 && buffer[0] === 0xff && buffer[1] === 0xfe) {
    return buffer.subarray(2).toString("utf16le");
  }
  if (buffer.length >= 2 && buffer[0] === 0xfe && buffer[1] === 0xff) {
    const body = Buffer.from(buffer.subarray(2));
    // Node has no UTF-16BE decoder; swapping the 16-bit code units to LE is exact for any
    // UTF-16 text. An odd byte count is not UTF-16 at all, so fall back and let JSON report it.
    if (body.length % 2 !== 0) return buffer.toString("utf8");
    body.swap16();
    return body.toString("utf16le");
  }
  return buffer.toString("utf8");
}

export async function loadConfigFile() {
  let text;
  try {
    text = decodeConfigText(await readFile(configFilePath()));
  } catch (error) {
    if (error.code === "ENOENT" || error.code === "ENOTDIR") return {};
    throw new ConfigError(`无法读取配置文件 ${configFilePath()}: ${error.message}`, "CONFIG_FILE_INVALID");
  }
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new ConfigError(`配置文件 ${configFilePath()} 不是有效 JSON: ${error.message}`, "CONFIG_FILE_INVALID");
  }
}

function fileValue(fileConfig, keys) {
  for (const key of keys) {
    const value = fileConfig?.[key];
    if (typeof value === "string" && value.trim()) return value.trim();
    if (typeof value === "number" && Number.isFinite(value)) return value;
    if (typeof value === "boolean") return value;
    if (Array.isArray(value)) return value;
  }
  return undefined;
}

function envOrFile(envName, fileConfig, keys, fallback) {
  const envValue = env(envName);
  if (envValue != null) return envValue;
  const configValue = fileValue(fileConfig, keys);
  return configValue == null ? fallback : configValue;
}

function envOrFileInt(envName, fileConfig, keys, fallback, { min = Number.MIN_SAFE_INTEGER } = {}) {
  const envValue = env(envName);
  if (envValue != null) return parseConfigInt(envValue, fallback, { min });
  const configValue = fileValue(fileConfig, keys);
  return configValue == null ? fallback : parseConfigInt(configValue, fallback, { min });
}

function envOrFileBool(envName, fileConfig, keys, fallback) {
  const envValue = env(envName);
  if (envValue != null) return parseBoolValue(envValue, fallback);
  const configValue = fileValue(fileConfig, keys);
  return configValue == null ? fallback : parseBoolValue(configValue, fallback);
}

function envOrFileList(envName, fileConfig, keys, fallback = []) {
  const envValue = env(envName);
  if (envValue != null) return parseListValue(envValue);
  const configValue = fileValue(fileConfig, keys);
  return configValue == null ? fallback : parseListValue(configValue);
}

function dedupeStrings(items) {
  const out = [];
  const seen = new Set();
  for (const item of items) {
    const value = String(item || "").trim();
    if (!value || seen.has(value)) continue;
    seen.add(value);
    out.push(value);
  }
  return out;
}

/**
 * Collect official Tavily keys.
 * Priority: TAVILY_API_KEYS env → TAVILY_API_KEY env → merge file tavilyApiKeys + tavilyApiKey.
 * Empty tavilyApiKeys: [] does NOT suppress a valid tavilyApiKey.
 * Proxy credentials are a different field and never land in this list.
 */
export function resolveTavilyApiKeys(fileConfig, getEnv = env) {
  const fromEnvMulti = getEnv("TAVILY_API_KEYS");
  if (fromEnvMulti != null && String(fromEnvMulti).trim() !== "") {
    return dedupeStrings(parseListValue(fromEnvMulti));
  }

  const fromEnvSingle = getEnv("TAVILY_API_KEY");
  if (fromEnvSingle != null && String(fromEnvSingle).trim() !== "") {
    return dedupeStrings(parseListValue(fromEnvSingle));
  }

  const multiRaw = fileValue(fileConfig, ["TAVILY_API_KEYS", "tavilyApiKeys", "tavily_api_keys"]);
  const singleRaw = fileValue(fileConfig, ["TAVILY_API_KEY", "tavilyApiKey", "tavily_api_key"]);
  const multi = multiRaw == null ? [] : dedupeStrings(parseListValue(multiRaw));
  const single = singleRaw == null ? [] : dedupeStrings(parseListValue(singleRaw));
  return dedupeStrings([...multi, ...single]);
}

/**
 * Collect official Firecrawl keys.
 * Priority: FIRECRAWL_API_KEYS env → FIRECRAWL_API_KEY env → merge file firecrawlApiKeys +
 * firecrawlApiKey. Empty firecrawlApiKeys: [] does NOT suppress a valid firecrawlApiKey.
 *
 * The pool is separate from the keyless tier: an empty result means "use keyless", which is a
 * different billing path (per-IP allowance) from an account-scoped key.
 */
export function resolveFirecrawlApiKeys(fileConfig, getEnv = env) {
  const fromEnvMulti = getEnv("FIRECRAWL_API_KEYS");
  if (fromEnvMulti != null && String(fromEnvMulti).trim() !== "") {
    return dedupeStrings(parseListValue(fromEnvMulti));
  }

  const fromEnvSingle = getEnv("FIRECRAWL_API_KEY");
  if (fromEnvSingle != null && String(fromEnvSingle).trim() !== "") {
    return dedupeStrings(parseListValue(fromEnvSingle));
  }

  const multiRaw = fileValue(fileConfig, ["FIRECRAWL_API_KEYS", "firecrawlApiKeys", "firecrawl_api_keys"]);
  const singleRaw = fileValue(fileConfig, ["FIRECRAWL_API_KEY", "firecrawlApiKey", "firecrawl_api_key"]);
  const multi = multiRaw == null ? [] : dedupeStrings(parseListValue(multiRaw));
  const single = singleRaw == null ? [] : dedupeStrings(parseListValue(singleRaw));
  return dedupeStrings([...multi, ...single]);
}

/**
 * Expand a leading `~` in a configured path. Both separators count: Windows shells and Explorer
 * hand out `~\dir` as readily as `~/dir`, and accepting only the POSIX form does not fail — it
 * silently creates a literal `~` directory relative to the cwd.
 */
export function resolveUserPath(value) {
  if (!value || typeof value !== "string") return value;
  if (value === "~") return homedir();
  if (value.startsWith("~/") || value.startsWith("~\\")) {
    return path.join(homedir(), value.slice(2));
  }
  return value;
}

/**
 * Extra-channel weights. The value may be a number (applied to every channel) or an object
 * keyed by channel name (`tavily`, `firecrawl`, `exa`, `fathom`, `mcpTavily`). Weights are
 * relative shares used to decide how many channels are worth calling when the budget is
 * tight; a weight of 0 (or a missing key) switches that channel off.
 */
export const DEFAULT_PROVIDER_WEIGHTS = {
  tavily: 1,
  firecrawl: 1,
  exa: 1,
  fathom: 1,
  mcpTavily: 1,
};

function normalizeWeight(value, fallback) {
  const parsed = typeof value === "number" ? value : Number.parseFloat(value);
  if (!Number.isFinite(parsed) || parsed < 0) return fallback;
  return parsed;
}

export function resolveProviderWeights(fileConfig, getEnv = env) {
  const fromEnv = getEnv("GROK_PROVIDER_WEIGHTS");
  // fileValue only accepts strings/numbers/booleans/arrays, so the object form is read
  // straight off the file here.
  const raw =
    fromEnv != null
      ? fromEnv
      : (() => {
          for (const key of ["GROK_PROVIDER_WEIGHTS", "providerWeights", "provider_weights"]) {
            const value = fileConfig?.[key];
            if (value != null && (typeof value === "object" || (typeof value === "string" && value.trim()))) return value;
          }
          return undefined;
        })();

  const weights = { ...DEFAULT_PROVIDER_WEIGHTS };
  if (raw == null) return weights;

  if (typeof raw === "number" || (typeof raw === "string" && raw.trim() && !raw.trim().startsWith("{"))) {
    const shared = normalizeWeight(raw, 1);
    for (const key of Object.keys(weights)) weights[key] = shared;
    return weights;
  }

  let parsed = raw;
  if (typeof raw === "string") {
    try {
      parsed = JSON.parse(raw);
    } catch {
      return weights;
    }
  }
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return weights;

  for (const key of Object.keys(weights)) {
    if (Object.hasOwn(parsed, key)) weights[key] = normalizeWeight(parsed[key], weights[key]);
  }
  // Unknown channel names are kept out of the resolved map: a typo should not silently
  // create a channel that no adapter implements.
  return weights;
}

export function inferApiProvider(grokApiUrl) {
  const normalized = String(grokApiUrl || "").toLowerCase();
  if (normalized.includes("openrouter")) return "openrouter";
  if (normalized.includes("api.x.ai")) return "xai";
  return "openai-compatible";
}

export function normalizeApiProvider(value, grokApiUrl) {
  const provider = String(value || inferApiProvider(grokApiUrl)).trim().toLowerCase();
  if (API_PROVIDERS.has(provider)) return provider;
  throw new ConfigError(`GROK_API_PROVIDER 必须是: ${[...API_PROVIDERS].join(", ")}`, "GROK_API_PROVIDER_INVALID");
}

export function normalizeSearchSource(value) {
  const source = String(value || DEFAULT_SEARCH_SOURCE).trim().toLowerCase();
  if (SEARCH_SOURCES.has(source)) return source;
  throw new ConfigError(`search source 必须是: ${[...SEARCH_SOURCES].join(", ")}`, "SEARCH_SOURCE_INVALID");
}

export function usesXSearch(searchSource) {
  return searchSource === "x" || searchSource === "both";
}

export function usesWebSearch(searchSource) {
  return searchSource === "web" || searchSource === "both";
}

export function normalizeOpenRouterSearchEngine(value) {
  const engine = String(value || DEFAULT_RESPONSES_OPENROUTER_ENGINE).trim().toLowerCase();
  if (OPENROUTER_SEARCH_ENGINES.has(engine)) return engine;
  throw new ConfigError(
    `GROK_RESPONSES_OPENROUTER_ENGINE 必须是: ${[...OPENROUTER_SEARCH_ENGINES].join(", ")}`,
    "GROK_RESPONSES_OPENROUTER_ENGINE_INVALID"
  );
}

// Options removed after a deprecation window. A truthy value used to change results (it
// attached X search), so ignoring it would fail silently; refuse to start instead. A false or
// missing value never did anything and stays accepted.
const REMOVED_OPTIONS = [
  {
    env: "GROK_RESPONSES_INCLUDE_X_SEARCH",
    keys: ["responsesIncludeXSearch", "responses_include_x_search", "GROK_RESPONSES_INCLUDE_X_SEARCH"],
    replacement: 'searchSource: "both"（或 GROK_SEARCH_SOURCE=both / --source both）',
  },
];

function rejectRemovedOptions(fileConfig) {
  for (const option of REMOVED_OPTIONS) {
    if (!envOrFileBool(option.env, fileConfig, option.keys, false)) continue;
    throw new ConfigError(`${option.keys[0]} / ${option.env} 已移除，请改用 ${option.replacement}`, "CONFIG_OPTION_REMOVED");
  }
}

export async function loadConfig({ requireGrok = false } = {}) {
  const fileConfig = await loadConfigFile();
  rejectRemovedOptions(fileConfig);
  const grokApiUrl = envOrFile("GROK_API_URL", fileConfig, ["GROK_API_URL", "grokApiUrl", "grok_api_url", "apiUrl", "api_url"]);
  const grokApiKey = envOrFile("GROK_API_KEY", fileConfig, ["GROK_API_KEY", "grokApiKey", "grok_api_key", "apiKey", "api_key"]);
  const rawApiProvider = envOrFile("GROK_API_PROVIDER", fileConfig, [
    "GROK_API_PROVIDER",
    "apiProvider",
    "api_provider",
    "grokApiProvider",
    "grok_api_provider",
  ]);

  if (requireGrok && !grokApiUrl) {
    throw new ConfigError("GROK_API_URL 未配置", "GROK_API_URL_MISSING");
  }
  if (requireGrok && !grokApiKey) {
    throw new ConfigError("GROK_API_KEY 未配置", "GROK_API_KEY_MISSING");
  }

  const apiProvider = requireGrok
    ? normalizeApiProvider(rawApiProvider, grokApiUrl)
    : rawApiProvider == null
      ? inferApiProvider(grokApiUrl)
      : String(rawApiProvider).trim().toLowerCase();

  const configuredModel = envOrFile("GROK_MODEL", fileConfig, ["GROK_MODEL", "grokModel", "grok_model", "model"], DEFAULT_MODEL);
  const outputDir = resolveUserPath(
    envOrFile("GROK_OUTPUT_DIR", fileConfig, ["GROK_OUTPUT_DIR", "outputDir", "output_dir"], DEFAULT_OUTPUT_DIR)
  );
  // Small cross-command state (provider cooldowns). Kept outside outputDir so the retention
  // sweep never deletes it.
  const stateDir = resolveUserPath(
    envOrFile("GROK_STATE_DIR", fileConfig, ["GROK_STATE_DIR", "stateDir", "state_dir"], DEFAULT_STATE_DIR)
  );

  return {
    grokApiUrl,
    grokApiKey,
    apiProvider,
    grokModel: configuredModel,
    responsesMaxTurns: envOrFileInt(
      "GROK_RESPONSES_MAX_TURNS",
      fileConfig,
      ["GROK_RESPONSES_MAX_TURNS", "responsesMaxTurns", "responses_max_turns"],
      DEFAULT_RESPONSES_MAX_TURNS,
      { min: 1 }
    ),
    // null = not sent; the relay decides. false is a cost lever where the relay passes it through.
    responsesParallelToolCalls: envOrFileBool(
      "GROK_RESPONSES_PARALLEL_TOOL_CALLS",
      fileConfig,
      ["GROK_RESPONSES_PARALLEL_TOOL_CALLS", "responsesParallelToolCalls", "responses_parallel_tool_calls"],
      null
    ),
    responsesReasoningEffort: envOrFile(
      "GROK_RESPONSES_REASONING_EFFORT",
      fileConfig,
      ["GROK_RESPONSES_REASONING_EFFORT", "responsesReasoningEffort", "responses_reasoning_effort"],
      DEFAULT_RESPONSES_REASONING_EFFORT
    ),
    responsesAllowedDomains: envOrFileList("GROK_RESPONSES_ALLOWED_DOMAINS", fileConfig, [
      "GROK_RESPONSES_ALLOWED_DOMAINS",
      "responsesAllowedDomains",
      "responses_allowed_domains",
    ]),
    responsesExcludedDomains: envOrFileList("GROK_RESPONSES_EXCLUDED_DOMAINS", fileConfig, [
      "GROK_RESPONSES_EXCLUDED_DOMAINS",
      "responsesExcludedDomains",
      "responses_excluded_domains",
    ]),
    responsesSearchSource: envOrFile(
      "GROK_SEARCH_SOURCE",
      fileConfig,
      ["GROK_SEARCH_SOURCE", "searchSource", "search_source"],
      ""
    ),
    responsesAllowedXHandles: envOrFileList("GROK_RESPONSES_ALLOWED_X_HANDLES", fileConfig, [
      "GROK_RESPONSES_ALLOWED_X_HANDLES",
      "responsesAllowedXHandles",
      "responses_allowed_x_handles",
    ]),
    responsesExcludedXHandles: envOrFileList("GROK_RESPONSES_EXCLUDED_X_HANDLES", fileConfig, [
      "GROK_RESPONSES_EXCLUDED_X_HANDLES",
      "responsesExcludedXHandles",
      "responses_excluded_x_handles",
    ]),
    responsesXImageUnderstanding: envOrFileBool("GROK_X_IMAGE_UNDERSTANDING", fileConfig, [
      "GROK_X_IMAGE_UNDERSTANDING",
      "xImageUnderstanding",
      "x_image_understanding",
    ], false),
    responsesXVideoUnderstanding: envOrFileBool("GROK_X_VIDEO_UNDERSTANDING", fileConfig, [
      "GROK_X_VIDEO_UNDERSTANDING",
      "xVideoUnderstanding",
      "x_video_understanding",
    ], false),
    responsesOpenRouterEngine: envOrFile(
      "GROK_RESPONSES_OPENROUTER_ENGINE",
      fileConfig,
      ["GROK_RESPONSES_OPENROUTER_ENGINE", "responsesOpenRouterEngine", "responses_openrouter_engine"],
      DEFAULT_RESPONSES_OPENROUTER_ENGINE
    ),
    tavilyApiUrl: envOrFile("TAVILY_API_URL", fileConfig, ["TAVILY_API_URL", "tavilyApiUrl", "tavily_api_url"], DEFAULT_TAVILY_API_URL),
    // Third-party Tavily-compatible base. Never put this URL in tavilyApiUrl: proxy tokens
    // and official tvly-* keys are not interchangeable.
    tavilyProxyUrl: envOrFile("TAVILY_PROXY_URL", fileConfig, ["TAVILY_PROXY_URL", "tavilyProxyUrl", "tavily_proxy_url"]),
    tavilyProxyKey: envOrFile("TAVILY_PROXY_KEY", fileConfig, ["TAVILY_PROXY_KEY", "tavilyProxyKey", "tavily_proxy_key"]),
    tavilyProxyTimeoutMs: envOrFileInt(
      "TAVILY_PROXY_TIMEOUT_MS",
      fileConfig,
      ["TAVILY_PROXY_TIMEOUT_MS", "tavilyProxyTimeoutMs", "tavily_proxy_timeout_ms"],
      12_000,
      { min: 1 }
    ),
    // Multi-key official pool. tavilyApiKey stays the first key for callers that still read one.
    ...((tavilyApiKeys) => ({
      tavilyApiKeys,
      tavilyApiKey: tavilyApiKeys[0],
    }))(resolveTavilyApiKeys(fileConfig)),

    firecrawlApiUrl: envOrFile(
      "FIRECRAWL_API_URL",
      fileConfig,
      ["FIRECRAWL_API_URL", "firecrawlApiUrl", "firecrawl_api_url"],
      DEFAULT_FIRECRAWL_API_URL
    ),
    // Multi-key official pool. firecrawlApiKey stays the first key for callers that still
    // read one; an empty pool means the keyless tier is used.
    ...((firecrawlApiKeys) => ({
      firecrawlApiKeys,
      firecrawlApiKey: firecrawlApiKeys[0] || "",
    }))(resolveFirecrawlApiKeys(fileConfig)),

    exaApiUrl: envOrFile("EXA_API_URL", fileConfig, ["EXA_API_URL", "exaApiUrl", "exa_api_url"], DEFAULT_EXA_API_URL),
    exaApiKey: envOrFile("EXA_API_KEY", fileConfig, ["EXA_API_KEY", "exaApiKey", "exa_api_key"]),

    // fathom: an MCP server that fans one query out across several web engines.
    fathomApiUrl: envOrFile("FATHOM_API_URL", fileConfig, ["FATHOM_API_URL", "fathomApiUrl", "fathom_api_url"]),
    fathomApiKey: envOrFile("FATHOM_API_KEY", fileConfig, ["FATHOM_API_KEY", "fathomApiKey", "fathom_api_key"]),
    // `mega_search` takes an engine list, `search` takes exactly one engine.
    fathomSearchTool: envOrFile("FATHOM_SEARCH_TOOL", fileConfig, ["FATHOM_SEARCH_TOOL", "fathomSearchTool", "fathom_search_tool"], "mega_search"),
    fathomEngines: envOrFile("FATHOM_ENGINES", fileConfig, ["FATHOM_ENGINES", "fathomEngines", "fathom_engines"]),
    // One budget for the whole fathom call, not per engine attempt: the adapter retries engine
    // plans in sequence, so a per-attempt timeout multiplies and can outlast the command deadline.
    fathomTimeoutMs: envOrFileInt(
      "FATHOM_TIMEOUT_MS",
      fileConfig,
      ["FATHOM_TIMEOUT_MS", "fathomTimeoutMs", "fathom_timeout_ms"],
      30_000,
      { min: 1 }
    ),

    // MCP-Tavily: a Tavily-compatible MCP relay (its own URL/token pair, separate from
    // the official Tavily keys and from the Tavily proxy above).
    mcpTavilyUrl: envOrFile("MCP_TAVILY_URL", fileConfig, ["MCP_TAVILY_URL", "mcpTavilyUrl", "mcp_tavily_url"]),
    mcpTavilyToken: envOrFile("MCP_TAVILY_TOKEN", fileConfig, ["MCP_TAVILY_TOKEN", "mcpTavilyToken", "mcp_tavily_token"]),
    mcpTavilyTool: envOrFile(
      "MCP_TAVILY_TOOL",
      fileConfig,
      ["MCP_TAVILY_TOOL", "mcpTavilyTool", "mcp_tavily_tool"],
      "search_proxy_tavily_search"
    ),

    // Relative search share per extra channel. Each channel still searches the full
    // --extra target; the weights only decide which channels are worth calling when the
    // budget is tight, and a weight of 0 switches a channel off.
    providerWeights: resolveProviderWeights(fileConfig),

    retryMaxAttempts: envInt("GROK_RETRY_MAX_ATTEMPTS", 3, { min: 1 }),
    retryMultiplier: envFloat("GROK_RETRY_MULTIPLIER", 1, { min: 0 }),
    retryMaxWait: envFloat("GROK_RETRY_MAX_WAIT", 10, { min: 0 }),
    defaultExtra: envOrFileInt("GROK_DEFAULT_EXTRA", fileConfig, ["GROK_DEFAULT_EXTRA", "defaultExtra", "default_extra"], DEFAULT_EXTRA, {
      min: 0,
    }),
    sourceChars: envOrFileInt("GROK_SOURCE_CHARS", fileConfig, ["GROK_SOURCE_CHARS", "sourceChars", "source_chars"], DEFAULT_SOURCE_CHARS, {
      min: 0,
    }),
    maxSources: envOrFileInt("GROK_MAX_SOURCES", fileConfig, ["GROK_MAX_SOURCES", "maxSources", "max_sources"], DEFAULT_MAX_SOURCES, {
      min: 1,
    }),
    deadlineSeconds: envOrFileInt(
      "GROK_DEADLINE_SECONDS",
      fileConfig,
      ["GROK_DEADLINE_SECONDS", "deadlineSeconds", "deadline_seconds"],
      DEFAULT_DEADLINE_SECONDS,
      { min: 0 }
    ),
    outputDir,
    stateDir,
    outputRetentionDays: DEFAULT_OUTPUT_RETENTION_DAYS,
    // One JSON record per command (query, options, answer, sources, usage, errors) so a run
    // can be replayed without a session export. `GROK_RUN_LOG=off` disables it.
    runLog: envOrFileBool("GROK_RUN_LOG", fileConfig, ["GROK_RUN_LOG", "runLog", "run_log"], true),
    // Also keep the raw Grok Responses body inside the run record.
    debugRaw: envBool("GROK_DEBUG_RAW", false),
    debug: envBool("GROK_DEBUG", false),
  };
}

export function maskSecret(value) {
  if (!value) return "未配置";
  if (value.length <= 8) return "***";
  return `${value.slice(0, 4)}${"*".repeat(value.length - 8)}${value.slice(-4)}`;
}
