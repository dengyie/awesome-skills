#!/usr/bin/env node
// Cooldown records must survive concurrent writes. A search runs its extra channels in parallel
// and a user can start two searches at once; an in-place write can be read mid-flight, and a
// torn JSON document parses as "no cooldown" — the protection disappears exactly when it is
// needed. The writer therefore swaps a temp file in by rename.
import assert from "node:assert/strict";
import { mkdtempSync, readdirSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { activeChannelCooldown, recordChannelCooldown, recordExaCooldown } from "../scripts/lib/cooldown.js";

const stateDir = mkdtempSync(path.join(tmpdir(), "grok-cooldown-atomic-"));
const config = { stateDir };
const leftovers = () => readdirSync(stateDir).filter((name) => name.endsWith(".tmp"));

// Many writers on the same file: last one wins, but the file is never half-written.
await Promise.all(
  Array.from({ length: 12 }, (_, i) =>
    recordChannelCooldown(config, "grok", {
      authMode: "https://relay/v1|grok-4.7",
      retryAfterMs: 60_000 + i,
      reason: `r${i}`,
    })
  )
);

const recordPath = path.join(stateDir, "grok-cooldown.json");
const parsed = JSON.parse(readFileSync(recordPath, "utf8"));
assert.ok(Number.isFinite(Date.parse(parsed.until)), "the record on disk must be complete JSON");
assert.match(parsed.reason, /^r\d+$/);

const active = await activeChannelCooldown(config, "grok", "https://relay/v1|grok-4.7");
assert.ok(active, "the cooldown must be readable right after concurrent writes");
assert.equal(active.reason, parsed.reason);

// Someone else's upstream (different auth mode) must not be blocked by this record.
assert.equal(await activeChannelCooldown(config, "grok", "https://other/v1|grok-4.7"), null);

// No temp files left behind, including when a swap raced.
assert.deepEqual(leftovers(), [], `temp files must not be left behind: ${leftovers().join(", ")}`);

// The single-record Exa writer goes through the same swap path.
await Promise.all(
  Array.from({ length: 6 }, () => recordExaCooldown(config, { retryAfterMs: 90_000, reason: "credits" }))
);
const exa = JSON.parse(readFileSync(path.join(stateDir, "exa-cooldown.json"), "utf8"));
assert.equal(exa.reason, "credits");
assert.deepEqual(leftovers(), []);

console.log("cooldown-atomic.test.js: ok");
