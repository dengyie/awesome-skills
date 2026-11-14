#!/usr/bin/env node
// Every test that needs an isolated home or state dir calls mkdtemp and leaves it behind, so one
// full `npm test` run drops roughly sixty `grok-*` directories into the OS temp dir. Any single
// directory is harmless, but they accumulate run after run (over a thousand on this machine), so
// the end of the chain sweeps them. `npm test` joins its steps with `&&`: a failing test stops the
// chain before this script, which is what you want — the dirs of the failing run stay for triage.
import { readdir, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";

const root = tmpdir();
const stale = (await readdir(root, { withFileTypes: true })).filter(
  (entry) => entry.isDirectory() && entry.name.startsWith("grok-")
);
await Promise.all(stale.map((entry) => rm(path.join(root, entry.name), { recursive: true, force: true })));
console.log(`cleanup-temp.js: removed ${stale.length} test dirs`);
