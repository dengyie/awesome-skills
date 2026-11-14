/**
 * Minimal JSON-RPC client for MCP (Model Context Protocol) streamable-HTTP servers.
 *
 * Both extra channels this package talks to (fathom, MCP-Tavily) expose their search
 * capability as an MCP tool rather than a plain REST endpoint, so the adapter needs the
 * handshake (`initialize`) followed by a `tools/call`. The servers answer with
 * `application/json` or `text/event-stream`; only the JSON form is used here, and a
 * server that insists on SSE is answered by parsing the `data:` lines out of the body.
 */
import { createRequire } from "node:module";
import { debugLog, redactSecrets } from "./http.js";

// Reported in the handshake. Read from package.json so a release bump cannot leave a stale
// version in the MCP client info.
const VERSION = createRequire(import.meta.url)("../../package.json").version;

const MCP_TIMEOUT_MS = 90_000;
// The handshake is a local JSON-RPC round trip that answers in milliseconds. It is capped well
// below the caller's budget so a silent server cannot consume half of it before the search
// request is even sent: a 30s fathom budget must stay a 30s budget for the whole call.
const MCP_HANDSHAKE_TIMEOUT_MS = 5_000;

/**
 * Whether a channel has both halves of an MCP credential. Each MCP channel keeps its own
 * URL and token fields, so the field names come from the caller.
 */
export function hasMcpConfig(config, { urlKey = "mcpUrl", tokenKey = "mcpToken" } = {}) {
  const url = typeof config?.[urlKey] === "string" ? config[urlKey].trim() : "";
  const token = typeof config?.[tokenKey] === "string" ? config[tokenKey].trim() : "";
  return Boolean(url && token);
}

/**
 * SSE responses carry the JSON-RPC frame in `data:` lines. Extract the last complete
 * JSON payload; a frame split across several `data:` lines is joined with newlines.
 */
function parseEventStream(body) {
  const payloads = [];
  for (const block of String(body || "").split(/\r?\n\r?\n/)) {
    const data = block
      .split(/\r?\n/)
      .filter((line) => line.startsWith("data:"))
      .map((line) => line.slice(5).trim())
      .join("\n");
    if (!data || data === "[DONE]") continue;
    try {
      payloads.push(JSON.parse(data));
    } catch {
      // A partial or non-JSON frame is not a response we can use.
    }
  }
  return payloads.length ? payloads[payloads.length - 1] : null;
}

function parseFrame(contentType, body) {
  if (contentType.includes("text/event-stream")) return parseEventStream(body);
  try {
    return JSON.parse(body);
  } catch {
    return null;
  }
}

/**
 * One JSON-RPC round trip. Returns the `result` object, or throws with the server's
 * own error message attached so the caller can report it the way it reports any other
 * provider failure.
 */
async function rpcCall(url, token, method, params, { timeoutMs = MCP_TIMEOUT_MS, config } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json, text/event-stream",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }),
      signal: controller.signal,
    });
    const body = await response.text();
    if (!response.ok) {
      // The body can echo the bearer token back (some relays do); redact before it
      // reaches an error message that ends up in the run record.
      const error = new Error(`HTTP ${response.status}: ${redactSecrets(body, config).slice(0, 300)}`);
      error.status = response.status;
      throw error;
    }
    const frame = parseFrame(response.headers.get("content-type") || "", body);
    if (!frame) throw new Error(`MCP 响应无法解析: ${redactSecrets(body, config).slice(0, 200)}`);
    if (frame.error) {
      const error = new Error(String(frame.error?.message || frame.error?.code || "MCP 调用失败"));
      error.code = frame.error?.code;
      throw error;
    }
    return frame.result;
  } catch (error) {
    if (error.name === "AbortError") {
      const timeout = new Error(`请求超时（>${Math.round(timeoutMs / 1000)}s）`);
      timeout.timedOut = true;
      throw timeout;
    }
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

/**
 * MCP servers keep no session across requests when they do not hand back a session id,
 * so the handshake is repeated per call. It is cheap: the servers answer `initialize`
 * in milliseconds.
 */
async function callTool(url, token, tool, args, options = {}) {
  const budgetMs = Number.isFinite(options.timeoutMs) ? options.timeoutMs : MCP_TIMEOUT_MS;
  const startedAt = Date.now();
  await rpcCall(url, token, "initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "grok-search", version: VERSION },
  }, { ...options, timeoutMs: Math.min(budgetMs, MCP_HANDSHAKE_TIMEOUT_MS) });

  // Whatever the handshake used comes out of the same budget: the two round trips are one
  // caller-visible wait, not two independent ones.
  const remainingMs = budgetMs - (Date.now() - startedAt);
  if (remainingMs <= 0) {
    const timeout = new Error(`请求超时（>${Math.round(budgetMs / 1000)}s）`);
    timeout.timedOut = true;
    throw timeout;
  }
  const result = await rpcCall(url, token, "tools/call", { name: tool, arguments: args }, {
    ...options,
    timeoutMs: remainingMs,
  });
  const content = Array.isArray(result?.content) ? result.content : [];
  const text = content
    .filter((item) => item?.type === "text" && typeof item.text === "string")
    .map((item) => item.text)
    .join("\n");

  if (result?.isError) {
    // Servers report a failed call either as isError plus a text body, or as a text body
    // that starts with "HTTP 502: {...}". Both carry the real reason in the text.
    throw new Error(text.slice(0, 400) || "MCP 工具调用失败");
  }
  return { text, structured: result?.structuredContent };
}

/**
 * Run an MCP search tool and return its parsed payload.
 *
 * The tool's answer is JSON in the text body for both servers. A tool that answers with
 * plain prose (no JSON) is returned as `{ text }` so the caller can decide what to do
 * with it instead of crashing on a parse error.
 */
export async function mcpSearch(url, token, tool, args, options = {}) {
  const { text, structured } = await callTool(url, token, tool, args, options);
  if (structured && typeof structured === "object") return structured;
  try {
    return JSON.parse(text);
  } catch {
    debugLog(options.config, `mcp tool ${tool} returned non-JSON text`);
    return { text };
  }
}
