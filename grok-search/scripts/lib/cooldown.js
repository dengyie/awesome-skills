import { mkdir, readFile, rename, unlink, writeFile } from "node:fs/promises";
import path from "node:path";

/**
 * Cross-command cooldown for provider quota exhaustion.
 *
 * Firecrawl's keyless tier answers quota exhaustion with HTTP 429, `reason: "credits"` and a
 * `retry_after_seconds` that is hours away (observed 4.5k–80k seconds: it is a rolling daily
 * allowance, not a burst limit). Every later command in that window would otherwise pay the
 * same failed request before falling back, and search extras would keep hitting it too. The
 * state lives in a small file so that the next process can skip the provider outright.
 *
 * Records are keyed by auth mode where a provider has more than one: a cooldown hit while
 * keyless must not block a run that has since been given an API key. Exa has a single
 * (required) key, so its records carry no auth-mode distinction.
 */

const FIRECRAWL_FILE_NAME = "firecrawl-cooldown.json";
const EXA_FILE_NAME = "exa-cooldown.json";
const GROK_FILE_NAME = "grok-cooldown.json";
const CHANNEL_FILE_NAMES = {
  grok: GROK_FILE_NAME,
  fathom: "fathom-cooldown.json",
  mcpTavily: "mcp-tavily-cooldown.json",
};
export const DEFAULT_COOLDOWN_MS = 15 * 60 * 1000;
export const MAX_COOLDOWN_MS = 24 * 60 * 60 * 1000;

function debug(config, message) {
  if (config?.debug) console.error(`[grok-search] ${message}`);
}

function providerFilePath(config, fileName) {
  return path.join(config.stateDir, fileName);
}

async function readCooldownRecord(config, filePath) {
  let record;
  try {
    record = JSON.parse(await readFile(filePath, "utf8"));
  } catch (error) {
    if (error.code !== "ENOENT") debug(config, `cooldown read skipped: ${error.message}`);
    return null;
  }

  const until = Date.parse(record?.until);
  if (!Number.isFinite(until)) return null;
  if (until <= Date.now()) {
    await unlink(filePath).catch(() => {});
    return null;
  }
  return { ...record, until: new Date(until).toISOString() };
}

/**
 * Replace a state file atomically. A plain in-place write can be read mid-flight by a parallel
 * search, and a torn JSON document parses as "no cooldown" — the protection silently disappears
 * exactly while two commands are running. Write a sibling temp file and rename it over the
 * target: rename is atomic within a volume on both POSIX and Windows.
 *
 * Windows additionally refuses to replace a file another process holds open, so a busy target is
 * retried briefly rather than dropping the record.
 */
async function replaceFile(tmpPath, filePath) {
  for (let attempt = 0; ; attempt += 1) {
    try {
      await rename(tmpPath, filePath);
      return;
    } catch (error) {
      const busy = error.code === "EPERM" || error.code === "EACCES" || error.code === "EBUSY";
      if (!busy || attempt >= 2) throw error;
      await new Promise((resolve) => setTimeout(resolve, 10));
    }
  }
}

// Parallel writes inside one process start in the same millisecond, so a pid+clock temp name
// would collide and let two writers interleave into the same temp file.
let tempCounter = 0;

async function writeCooldownRecord(config, filePath, record) {
  tempCounter += 1;
  const tmpPath = `${filePath}.${process.pid}.${tempCounter}.tmp`;
  try {
    await mkdir(config.stateDir, { recursive: true, mode: 0o700 });
    await writeFile(tmpPath, JSON.stringify(record, null, 2), { encoding: "utf8", mode: 0o600 });
    await replaceFile(tmpPath, filePath);
  } catch (error) {
    // Do not leave the temp file behind when the swap failed.
    await unlink(tmpPath).catch(() => {});
    debug(config, `cooldown write skipped: ${error.message}`);
  }
}

async function clearCooldownFile(config, filePath) {
  try {
    await unlink(filePath);
  } catch (error) {
    if (error.code !== "ENOENT") debug(config, `cooldown clear skipped: ${error.message}`);
  }
}

function buildCooldownRecord({ authMode, retryAfterMs, reason }) {
  const waitMs =
    Number.isFinite(retryAfterMs) && retryAfterMs > 0 ? Math.min(retryAfterMs, MAX_COOLDOWN_MS) : DEFAULT_COOLDOWN_MS;
  const now = Date.now();
  return {
    until: new Date(now + waitMs).toISOString(),
    ...(authMode ? { auth_mode: authMode } : {}),
    reason: reason || "credits",
    hit_at: new Date(now).toISOString(),
  };
}

export function cooldownFilePath(config) {
  return providerFilePath(config, FIRECRAWL_FILE_NAME);
}

/**
 * Firecrawl cooldown state, one record per key.
 *
 * The state file holds a record per key because a key pool makes the allowance per key: key A
 * running out of credits says nothing about key B, and a single shared record would switch the
 * whole channel off as soon as one key is spent. The keyless tier has no key material, so it
 * keeps its own record under the `keyless` slot.
 *
 * Shape: `{ keyless: record | null, keys: { <fingerprint>: record } }`.
 */
export async function readFirecrawlCooldownState(config) {
  if (!config?.stateDir) return { keyless: null, keys: {} };

  let parsed;
  try {
    parsed = JSON.parse(await readFile(cooldownFilePath(config), "utf8"));
  } catch (error) {
    if (error.code !== "ENOENT") debug(config, `cooldown read skipped: ${error.message}`);
    return { keyless: null, keys: {} };
  }

  const now = Date.now();
  let pruned = false;
  const keep = (record) => {
    const until = Date.parse(record?.until);
    if (!Number.isFinite(until)) return null;
    if (until <= now) {
      pruned = true;
      return null;
    }
    return { ...record, until: new Date(until).toISOString() };
  };

  let keyless = keep(parsed?.keyless);
  const keys = {};
  const rawKeys =
    parsed?.keys && typeof parsed.keys === "object" && !Array.isArray(parsed.keys) ? parsed.keys : {};
  for (const [fingerprint, record] of Object.entries(rawKeys)) {
    const alive = keep(record);
    if (alive) keys[fingerprint] = alive;
    else pruned = true;
  }

  // A file written before the key pool held a single record at the top level. Treat it as the
  // keyless record so an in-flight cooldown is not lost on upgrade.
  if (!parsed?.keyless && !parsed?.keys && parsed?.until) {
    const legacy = keep(parsed);
    if (legacy) {
      keyless = legacy;
      pruned = true;
    }
  }

  if (pruned) {
    // Drop expired entries so the file does not keep dead keys around.
    await writeCooldownRecord(config, cooldownFilePath(config), { keyless, keys });
  }
  return { keyless, keys };
}

/**
 * The cooldown record for one scope. Without a fingerprint this is the keyless record; with
 * one it is the record for that key.
 */
export async function readFirecrawlCooldown(config, fingerprint) {
  const state = await readFirecrawlCooldownState(config);
  if (fingerprint) return state.keys[fingerprint] || null;
  return state.keyless || null;
}

/** The active cooldown for this scope, or null. */
export async function activeFirecrawlCooldown(config, authMode, fingerprint) {
  if (!config?.stateDir) return null;
  const record = await readFirecrawlCooldown(config, fingerprint);
  if (!record) return null;
  // Without a fingerprint the record is the keyless one, and the auth mode still has to match:
  // a keyless cooldown must not block a run that has since been given an API key.
  if (!fingerprint && authMode && record.auth_mode !== authMode) return null;
  return record;
}

export async function recordFirecrawlCooldown(config, { authMode, fingerprint, retryAfterMs, reason } = {}) {
  if (!config?.stateDir) return null;
  const record = buildCooldownRecord({ authMode: authMode || "keyless", retryAfterMs, reason });
  const state = await readFirecrawlCooldownState(config);
  if (fingerprint) {
    state.keys[fingerprint] = { ...record, key_fingerprint: fingerprint };
  } else {
    state.keyless = record;
  }
  await writeCooldownRecord(config, cooldownFilePath(config), { keyless: state.keyless, keys: state.keys });
  return record;
}

/**
 * Clear one scope. With a fingerprint it clears that key's cooldown; without one it clears the
 * keyless cooldown. A key that recovers must not wipe the cooldowns of its pool siblings.
 */
export async function clearFirecrawlCooldown(config, fingerprint) {
  if (!config?.stateDir) return;
  if (fingerprint) {
    const state = await readFirecrawlCooldownState(config);
    if (!state.keys[fingerprint]) return;
    delete state.keys[fingerprint];
    await writeCooldownRecord(config, cooldownFilePath(config), { keyless: state.keyless, keys: state.keys });
    return;
  }
  const state = await readFirecrawlCooldownState(config);
  if (!state.keyless) return;
  state.keyless = null;
  await writeCooldownRecord(config, cooldownFilePath(config), { keyless: null, keys: state.keys });
}

export function exaCooldownFilePath(config) {
  return providerFilePath(config, EXA_FILE_NAME);
}

export async function activeExaCooldown(config) {
  if (!config?.stateDir) return null;
  return readCooldownRecord(config, exaCooldownFilePath(config));
}

export async function recordExaCooldown(config, { retryAfterMs, reason } = {}) {
  if (!config?.stateDir) return null;
  const record = buildCooldownRecord({ authMode: "api_key", retryAfterMs, reason });
  await writeCooldownRecord(config, exaCooldownFilePath(config), record);
  return record;
}

export async function clearExaCooldown(config) {
  if (!config?.stateDir) return;
  await clearCooldownFile(config, exaCooldownFilePath(config));
}

/**
 * Generic per-channel cooldown used by the Grok upstream and by the MCP search channels.
 *
 * These channels have no quota API to ask: the only signal that a channel is unhealthy is
 * that its own request failed. A dead Grok relay would otherwise be re-billed on every
 * single command, so a failure opens a cooldown that later commands skip. The record is
 * keyed by `auth_mode` (the endpoint + model for Grok, the URL for an MCP channel) so a
 * configuration change takes effect immediately instead of waiting out the old cooldown.
 */
export function channelCooldownFilePath(config, channel) {
  const fileName = CHANNEL_FILE_NAMES[channel];
  if (!fileName) throw new Error(`未知 cooldown 通道: ${channel}`);
  return providerFilePath(config, fileName);
}

export async function activeChannelCooldown(config, channel, authMode) {
  if (!config?.stateDir) return null;
  const record = await readCooldownRecord(config, channelCooldownFilePath(config, channel));
  if (!record) return null;
  // Records are written from the trimmed endpoint, while the caller may pass the raw config
  // value (trailing spaces in a JSON string are easy to keep). Comparing untrimmed would make
  // the cooldown silently ineffective, so both sides are normalized here.
  if (authMode && record.auth_mode !== String(authMode).trim()) return null;
  return record;
}

export async function recordChannelCooldown(config, channel, { authMode, retryAfterMs, reason } = {}) {
  if (!config?.stateDir) return null;
  const record = buildCooldownRecord({ authMode, retryAfterMs, reason });
  await writeCooldownRecord(config, channelCooldownFilePath(config, channel), record);
  return record;
}

/**
 * Clear a channel cooldown. With an auth mode only that endpoint's record is cleared: a success
 * on a new endpoint says nothing about the old one, and wiping it would hide a still-broken URL
 * if the caller switches back.
 */
export async function clearChannelCooldown(config, channel, authMode) {
  if (!config?.stateDir) return;
  if (authMode) {
    const record = await readCooldownRecord(config, channelCooldownFilePath(config, channel));
    if (record?.auth_mode && record.auth_mode !== String(authMode).trim()) return;
  }
  await clearCooldownFile(config, channelCooldownFilePath(config, channel));
}

export function cooldownSkipMessage(record) {
  return `cooldown until ${record.until} (${record.reason || "credits"})`;
}
