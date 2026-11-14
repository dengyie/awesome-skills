import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { homedir } from "node:os";
import path from "node:path";
import { activeFirecrawlCooldown, clearFirecrawlCooldown, readFirecrawlCooldownState, recordFirecrawlCooldown } from "./cooldown.js";
import { authHeaders, backoffMs, debugLog, isPlainObject, requestJson, retryMaxAttempts, sleep, upstreamMessage } from "./http.js";
import { domainFilters } from "./sources.js";

const DEFAULT_FIRECRAWL_RR_PATH = path.join(homedir(), ".cache", "grok-search", "firecrawl-rr.json");

/**
 * Every official key in the pool. An empty result means the keyless tier is used, which bills
 * against a per-IP allowance instead of an account.
 */
export function allFirecrawlKeys(config) {
  if (Array.isArray(config?.firecrawlApiKeys) && config.firecrawlApiKeys.length) {
    return config.firecrawlApiKeys.map((key) => String(key || "").trim()).filter(Boolean);
  }
  if (typeof config?.firecrawlApiKey === "string" && config.firecrawlApiKey.trim()) {
    return [config.firecrawlApiKey.trim()];
  }
  return [];
}

export function hasFirecrawlApiKey(config) {
  return allFirecrawlKeys(config).length > 0;
}

export function firecrawlAuthMode(config) {
  return hasFirecrawlApiKey(config) ? "api_key" : "keyless";
}

/**
 * A short, stable fingerprint of a key.
 *
 * The cooldown state is keyed by this instead of by the key itself, so the state file never
 * holds key material, but a rotated or replaced key still gets its own cooldown record. The
 * digest is truncated: it only has to tell two keys apart, not resist an attacker who already
 * has the state file.
 */
export function firecrawlKeyFingerprint(key) {
  const value = String(key || "").trim();
  if (!value) return "";
  return createHash("sha256").update(value).digest("hex").slice(0, 16);
}

export function firecrawlRoundRobinPath(config) {
  if (typeof config?.firecrawlRoundRobinPath === "string" && config.firecrawlRoundRobinPath.trim()) {
    return config.firecrawlRoundRobinPath.trim();
  }
  return DEFAULT_FIRECRAWL_RR_PATH;
}

/** Read the persistent next index; returns 0 when the file is missing or corrupt. */
export function loadFirecrawlRoundRobinIndex(keyCount, config) {
  if (!Number.isFinite(keyCount) || keyCount <= 0) return 0;
  try {
    const data = JSON.parse(readFileSync(firecrawlRoundRobinPath(config), "utf8"));
    const n = Number(data?.nextIndex);
    if (!Number.isFinite(n) || n < 0) return 0;
    return Math.trunc(n) % keyCount;
  } catch {
    return 0;
  }
}

/** Persist the next index for later CLI processes. Best-effort. */
export function saveFirecrawlRoundRobinIndex(nextIndex, config) {
  try {
    const filePath = firecrawlRoundRobinPath(config);
    mkdirSync(path.dirname(filePath), { recursive: true });
    const payload = `${JSON.stringify({ nextIndex: Math.max(0, Math.trunc(nextIndex)), updatedAt: new Date().toISOString() })}\n`;
    writeFileSync(filePath, payload, { encoding: "utf8", mode: 0o600 });
  } catch {
    // RR degrades to always-start-at-0.
  }
}

/**
 * Claim the next key slot. The cursor advances immediately so the next CLI run starts on a
 * different key, which spreads the per-key allowance over the pool instead of burning the first
 * key on every command.
 */
export function nextFirecrawlApiKey(config) {
  const keys = allFirecrawlKeys(config);
  if (!keys.length) return null;
  const index = loadFirecrawlRoundRobinIndex(keys.length, config);
  saveFirecrawlRoundRobinIndex(index + 1, config);
  return { key: keys[index], index, total: keys.length };
}

/**
 * Firecrawl signals an exhausted allowance with 402, or 429 plus `reason: "credits"`.
 *
 * A bare 429 is a transient rate limit: it says nothing about the key's allowance, so it must
 * not rotate the pool.
 */
export function isFirecrawlQuotaError(error) {
  return error?.status === 402 || error?.upstreamCode === "credits";
}

/**
 * Whether a failed key should be abandoned in favour of the next one in the pool.
 *
 * An exhausted allowance (402 / `reason: "credits"`) is the key's own fault. An invalid key
 * (401) is a configuration mistake, but in a pool it is better to fall through to a working
 * sibling than to fail the whole channel; the invalid key is put in cooldown so it is not
 * picked again. A transient 5xx or a timeout is nobody's fault and is returned as is.
 */
export function isFirecrawlKeySpentError(error) {
  if (isFirecrawlQuotaError(error)) return true;
  return error?.status === 401;
}

function firecrawlHeadersForKey(apiKey) {
  return apiKey ? authHeaders(apiKey) : { "Content-Type": "application/json" };
}

function firstText(...values) {
  for (const value of values) {
    if (typeof value === "string" && value.trim()) return value.trim();
    if (typeof value === "number" && Number.isFinite(value)) return value;
  }
  return undefined;
}

/**
 * Firecrawl returns the page's meta tags alongside the markdown. Title, author and publish
 * date are exactly what a source card is otherwise missing, so surface them under stable
 * names instead of dropping the whole object.
 */
export function firecrawlMetadata(data) {
  const meta = data?.data?.metadata ?? data?.metadata;
  if (!isPlainObject(meta)) return {};
  const out = {
    title: firstText(meta.title, meta.ogTitle, meta["og:title"], meta["twitter:title"]),
    description: firstText(meta.description, meta.ogDescription, meta["og:description"], meta["twitter:description"]),
    author: firstText(meta.author, meta["article:author"], meta["twitter:creator"], meta.creator),
    published_at: firstText(
      meta.publishedTime,
      meta["article:published_time"],
      meta.datePublished,
      meta["og:article:published_time"],
      meta.publishedDate
    ),
    language: firstText(meta.language, meta["og:locale"]),
    status: firstText(meta.statusCode),
    source_url: firstText(meta.sourceURL, meta.url, meta["og:url"]),
  };
  for (const [key, value] of Object.entries(out)) {
    if (value === undefined) delete out[key];
  }
  return out;
}

/**
 * The channel-level cooldown: the record that means "do not call Firecrawl at all".
 *
 * With a key pool the allowance is per key, so one spent key says nothing about its siblings.
 * The channel is only dead when every key in the pool is cooling (or, without a pool, when the
 * keyless tier is). A single cooling key is skipped inside the pool instead of switching the
 * whole channel off.
 */
export async function firecrawlChannelCooldown(config) {
  if (!config?.stateDir) return null;
  const state = await readFirecrawlCooldownState(config);
  const keys = allFirecrawlKeys(config);
  if (!keys.length) return state.keyless || null;
  const fingerprints = keys.map((key) => firecrawlKeyFingerprint(key));
  const cooling = fingerprints.filter((fingerprint) => state.keys[fingerprint]);
  if (cooling.length === fingerprints.length) return state.keys[fingerprints[0]] || null;
  return null;
}

/**
 * Run fn(apiKey, index, total).
 *
 * Without a pool there is one keyless attempt: a quota error records the keyless cooldown.
 *
 * With a pool the run starts at the persistent round-robin index, so consecutive commands
 * spread over the keys instead of always burning the first one. A key that reports exhausted
 * credits is put in cooldown and the next key takes over. A key that is already cooling is
 * skipped, unless every key is cooling — then the request is still made, because an explicit
 * `--provider firecrawl` may follow a top-up that the state file cannot know about.
 */
export async function withFirecrawlApiKey(config, fn) {
  const keys = allFirecrawlKeys(config);
  const authMode = firecrawlAuthMode(config);

  if (!keys.length) {
    try {
      const result = await fn(null, -1, 0);
      // A keyless tier that works again (the daily allowance rolled over) must not stay in
      // cooldown, or the channel would be skipped for the rest of the window.
      if (result?.ok) await clearFirecrawlCooldown(config);
      return { ...result, firecrawl_key_index: -1, firecrawl_key_total: 0, firecrawl_keys_tried: 1 };
    } catch (error) {
      const quota = isFirecrawlQuotaError(error);
      if (quota) {
        await recordFirecrawlCooldown(config, {
          authMode,
          retryAfterMs: error.retryAfterMs,
          reason: error.upstreamCode || "quota",
        });
      }
      return {
        ok: false,
        error: error?.message || String(error),
        ...(quota ? { quota_exhausted: true } : {}),
        firecrawl_key_index: -1,
        firecrawl_key_total: 0,
        firecrawl_keys_tried: 1,
      };
    }
  }

  const cooling = new Set();
  for (const [offset, key] of keys.entries()) {
    const fingerprint = firecrawlKeyFingerprint(key);
    if (await activeFirecrawlCooldown(config, authMode, fingerprint)) cooling.add(offset);
  }
  const allCooling = cooling.size === keys.length;

  const claimed = nextFirecrawlApiKey(config);
  const start = claimed?.index ?? 0;
  let tried = 0;
  let lastError = "Firecrawl request failed";
  let lastUsed = start;

  for (let offset = 0; offset < keys.length; offset += 1) {
    const index = (start + offset) % keys.length;
    const apiKey = keys[index];

    if (cooling.has(index) && !allCooling) {
      debugLog(config, `firecrawl key#${index} in cooldown, try another key`);
      lastError = "Firecrawl key 在冷却中";
      continue;
    }

    tried += 1;
    lastUsed = index;
    try {
      const result = await fn(apiKey, index, keys.length);
      // A key that works again (a top-up) must not stay in cooldown. Only a real success
      // clears it: a soft failure (upstream said success:false) proves nothing about the
      // key's allowance, so it must not wipe a legitimate cooldown record.
      if (result?.ok) await clearFirecrawlCooldown(config, firecrawlKeyFingerprint(apiKey));
      saveFirecrawlRoundRobinIndex(lastUsed + 1, config);
      return {
        ...result,
        firecrawl_key_index: index,
        firecrawl_key_total: keys.length,
        firecrawl_keys_tried: tried,
      };
    } catch (error) {
      lastError = error?.message || String(error);
      saveFirecrawlRoundRobinIndex(lastUsed + 1, config);
      if (!isFirecrawlKeySpentError(error)) {
        return {
          ok: false,
          error: lastError,
          firecrawl_key_index: index,
          firecrawl_key_total: keys.length,
          firecrawl_keys_tried: tried,
        };
      }

      await recordFirecrawlCooldown(config, {
        authMode,
        fingerprint: firecrawlKeyFingerprint(apiKey),
        retryAfterMs: error.retryAfterMs,
        reason: error.upstreamCode || "quota",
      });
      if (offset < keys.length - 1) {
        debugLog(config, `firecrawl key#${index} exhausted, try next key: ${lastError}`);
        continue;
      }
      return {
        ok: false,
        error: lastError,
        quota_exhausted: true,
        firecrawl_key_index: index,
        firecrawl_key_total: keys.length,
        firecrawl_keys_tried: tried,
      };
    }
  }

  saveFirecrawlRoundRobinIndex(lastUsed + 1, config);
  return {
    ok: false,
    error: lastError,
    skipped: true,
    firecrawl_key_index: -1,
    firecrawl_key_total: keys.length,
    firecrawl_keys_tried: tried,
  };
}

/**
 * Retry policy has two layers. HTTP-level failures (5xx, transient 429, timeouts) belong to
 * `requestJson`, which also knows when a Retry-After is too far away to bother. The loop here
 * covers exactly one case: a 200 with empty markdown, which usually means a JS-rendered page
 * that needed a longer `waitFor`. Definite refusals (`success: false`), malformed JSON and
 * exhausted quota are returned at once; retrying them only spends requests and credits.
 */
export async function firecrawlScrape(url, config, { timeoutMs = 90_000 } = {}) {
  const endpoint = `${config.firecrawlApiUrl.replace(/\/+$/, "")}/scrape`;
  const authMode = firecrawlAuthMode(config);
  const startedAt = Date.now();
  const stats = { requests: 0 };

  const outcome = await withFirecrawlApiKey(config, async (apiKey) => {
    const maxAttempts = retryMaxAttempts(config);
    for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
      const data = await requestJson(endpoint, {
        headers: firecrawlHeadersForKey(apiKey),
        body: {
          url,
          formats: ["markdown"],
          timeout: 60_000,
          waitFor: (attempt + 1) * 1500,
        },
        timeoutMs,
        config,
        retry: true,
        // A 90s scrape timeout retried three times overruns the 240s command deadline; the
        // caller then sees DEADLINE_EXCEEDED instead of the real cause.
        retryOnTimeout: false,
        stats,
      });

      if (data?.success === false) {
        return { ok: false, error: upstreamMessage(data) || "Firecrawl Scrape 返回 success:false" };
      }

      const content = data?.data?.markdown || data?.markdown || "";
      if (content.trim()) {
        return {
          ok: true,
          content,
          raw: data,
          attempts: attempt + 1,
          metadata: firecrawlMetadata(data),
          ...(Number.isFinite(data?.data?.metadata?.creditsUsed) ? { credits_used: data.data.metadata.creditsUsed } : {}),
        };
      }

      debugLog(config, `Firecrawl empty markdown, retry ${attempt + 1}/${maxAttempts}`);
      if (attempt < maxAttempts - 1) await sleep(backoffMs(config, attempt));
    }

    return { ok: false, error: "Firecrawl Scrape 返回空内容" };
  });

  const base = {
    provider: "firecrawl",
    auth_mode: authMode,
    requests: stats.requests,
    duration_ms: Date.now() - startedAt,
    ...(outcome.quota_exhausted ? { quota_exhausted: true } : {}),
    ...(outcome.skipped ? { skipped: true } : {}),
    ...(Number.isFinite(outcome.firecrawl_key_index) ? { firecrawl_key_index: outcome.firecrawl_key_index } : {}),
    ...(Number.isFinite(outcome.firecrawl_key_total) ? { firecrawl_key_total: outcome.firecrawl_key_total } : {}),
    ...(Number.isFinite(outcome.firecrawl_keys_tried) ? { firecrawl_keys_tried: outcome.firecrawl_keys_tried } : {}),
  };

  // The success shape carries no `error` key at all. The downstream failure summary filters
  // on the presence of `error` rather than on `ok`, so a stray error field would make a
  // successful provider look like the cause of someone else's failure.
  if (!outcome.ok) {
    return { ...base, ok: false, error: outcome.error || "Firecrawl request failed" };
  }
  return {
    ...base,
    ok: true,
    content: outcome.content,
    raw: outcome.raw,
    attempts: outcome.attempts,
    metadata: outcome.metadata,
    ...(outcome.credits_used == null ? {} : { credits_used: outcome.credits_used }),
  };
}
function sourceFromFirecrawl(result) {
  const url = typeof result?.url === "string" ? result.url.trim() : "";
  if (!url) return null;
  return {
    url,
    provider: "firecrawl",
    ...(result.title ? { title: String(result.title).trim() } : {}),
    ...(result.description ? { description: String(result.description).trim() } : {}),
  };
}

export async function firecrawlSearch(query, limit, config, filters = {}) {
  const endpoint = `${config.firecrawlApiUrl.replace(/\/+$/, "")}/search`;
  const authMode = firecrawlAuthMode(config);
  const { allowed, excluded } = domainFilters(filters);
  const stats = { requests: 0 };

  const outcome = await withFirecrawlApiKey(config, async (apiKey) => {
    const data = await requestJson(endpoint, {
      headers: firecrawlHeadersForKey(apiKey),
      body: {
        query,
        limit,
        // Firecrawl v2 search: includeDomains / excludeDomains are hostnames and mutually
        // exclusive, which resolveFilterPair already guarantees upstream.
        ...(allowed.length ? { includeDomains: allowed } : {}),
        ...(excluded.length ? { excludeDomains: excluded } : {}),
      },
      timeoutMs: 90_000,
      config,
      retry: true,
      // Same reason as the scrape path below: three 90s timeouts overrun the 240s command
      // deadline, and the caller then loses a Grok answer it already paid for.
      retryOnTimeout: false,
      stats,
    });

    // HTTP 200 with `success: false` is a refusal, not an empty result set. Reporting it as
    // success also lets `withFirecrawlApiKey` clear a live cooldown on the strength of a
    // request that never ran.
    if (data?.success === false) {
      return { ok: false, error: upstreamMessage(data) || "Firecrawl Search 返回 success:false" };
    }

    const rawResults = Array.isArray(data?.data?.web)
      ? data.data.web
      : Array.isArray(data?.data)
        ? data.data
        : Array.isArray(data?.web)
          ? data.web
          : [];
    const sources = rawResults.map(sourceFromFirecrawl).filter(Boolean);
    return {
      ok: true,
      sources,
      raw: data,
      ...(Number.isFinite(data?.creditsUsed) ? { credits_used: data.creditsUsed } : {}),
    };
  });

  const base = {
    provider: "firecrawl",
    auth_mode: authMode,
    requests: stats.requests,
    ...(outcome.quota_exhausted ? { quota_exhausted: true } : {}),
    ...(outcome.skipped ? { skipped: true } : {}),
    ...(Number.isFinite(outcome.firecrawl_key_index) ? { firecrawl_key_index: outcome.firecrawl_key_index } : {}),
    ...(Number.isFinite(outcome.firecrawl_key_total) ? { firecrawl_key_total: outcome.firecrawl_key_total } : {}),
    ...(Number.isFinite(outcome.firecrawl_keys_tried) ? { firecrawl_keys_tried: outcome.firecrawl_keys_tried } : {}),
  };

  // No `error` key on success: the downstream failure summary filters on the presence of
  // `error`, so a stray error field would make a successful provider look like the cause of
  // someone else's failure.
  if (!outcome.ok) {
    return { ...base, ok: false, error: outcome.error || "Firecrawl request failed", sources: [] };
  }
  return {
    ...base,
    ok: true,
    sources: outcome.sources,
    raw: outcome.raw,
    ...(outcome.credits_used == null ? {} : { credits_used: outcome.credits_used }),
  };
}
