import { mkdir, readFile, unlink, writeFile } from "node:fs/promises";
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

async function writeCooldownRecord(config, filePath, record) {
  try {
    await mkdir(config.stateDir, { recursive: true, mode: 0o700 });
    await writeFile(filePath, JSON.stringify(record, null, 2), { encoding: "utf8", mode: 0o600 });
  } catch (error) {
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

export async function readFirecrawlCooldown(config) {
  if (!config?.stateDir) return null;
  return readCooldownRecord(config, cooldownFilePath(config));
}

/** The active cooldown for this auth mode, or null. */
export async function activeFirecrawlCooldown(config, authMode) {
  const record = await readFirecrawlCooldown(config);
  return record && record.auth_mode === authMode ? record : null;
}

export async function recordFirecrawlCooldown(config, { authMode, retryAfterMs, reason } = {}) {
  if (!config?.stateDir) return null;
  const record = buildCooldownRecord({ authMode: authMode || "keyless", retryAfterMs, reason });
  await writeCooldownRecord(config, cooldownFilePath(config), record);
  return record;
}

export async function clearFirecrawlCooldown(config) {
  if (!config?.stateDir) return;
  await clearCooldownFile(config, cooldownFilePath(config));
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

export function cooldownSkipMessage(record) {
  return `cooldown until ${record.until} (${record.reason || "credits"})`;
}
