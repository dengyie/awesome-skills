#!/usr/bin/env node
// `~` expansion for configured paths (GROK_OUTPUT_DIR / GROK_STATE_DIR).
// Windows shells and Explorer hand out `~\state` as readily as `~/state`. Accepting only the
// POSIX form does not fail loudly: it writes a literal `~` directory under the cwd, so state
// and outputs silently land somewhere nobody looks.
import assert from "node:assert/strict";
import { homedir } from "node:os";
import path from "node:path";
import { resolveUserPath } from "../scripts/lib/config.js";

const home = homedir();

assert.equal(resolveUserPath("~"), home);
assert.equal(resolveUserPath("~/state"), path.join(home, "state"));
assert.equal(resolveUserPath("~\\state"), path.join(home, "state"), "the backslash form must expand too");
assert.equal(resolveUserPath("~\\a\\b"), path.join(home, "a", "b"));

// Absolute and cwd-relative paths are passed through untouched.
const absolute = process.platform === "win32" ? "C:\\Users\\nobody\\state" : "/srv/state";
assert.equal(resolveUserPath(absolute), absolute);
assert.equal(resolveUserPath("./state"), "./state");

// Empty/missing values and non-strings keep their identity so callers can apply their own default.
assert.equal(resolveUserPath(""), "");
assert.equal(resolveUserPath(null), null);
assert.equal(resolveUserPath(undefined), undefined);

// A `~` that is not a leading home segment belongs to the name.
assert.equal(resolveUserPath("/srv/~backup"), "/srv/~backup");
assert.equal(resolveUserPath("~backup"), "~backup");

console.log("config-paths.test.js: ok");
