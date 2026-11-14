#!/usr/bin/env node
// The degraded paths are what users actually hit when the relay is unhealthy, and they are only
// reachable through the CLI: exit code, answer body, diagnostics and the persisted cooldown all
// have to agree. A stub upstream supplies the failure shapes so this runs offline.
//
// Each scenario gets its own state dir: cooldowns are keyed by endpoint+model, so reusing one dir
// would make scenario 1's cooldown block scenario 2 instead of only its own follow-up request.
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { execFile } from "node:child_process";
import { mkdtemp, readFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

let mode = "500";
let hits = 0;

const server = createServer((req, res) => {
  let raw = "";
  req.on("data", (chunk) => {
    raw += chunk;
  });
  req.on("end", () => {
    hits += 1;
    if (mode === "500") {
      res.writeHead(500, { "content-type": "application/json" });
      res.end(JSON.stringify({ error: { message: "stub upstream exploded", code: "stub_500" } }));
      return;
    }
    const body =
      mode === "textonly"
        ? { model: "grok-4.7", output: [{ type: "message", content: [{ type: "output_text", text: "Stub answer from memory." }] }] }
        : {
            status: "incomplete",
            incomplete_details: { reason: "max_output_tokens" },
            model: "grok-4.7",
            output: [
              { type: "web_search_call", status: "completed", action: { type: "search", query: "q" } },
              { type: "message", content: [{ type: "output_text", text: "Stub partial answer" }] },
            ],
          };
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify(body));
  });
});
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const endpoint = `http://127.0.0.1:${server.address().port}/v1`;

// Home is isolated too, so the user's config.json (real keys, real extras) never participates.
const testHome = await mkdtemp(path.join(tmpdir(), "grok-cli-degrade-home-"));
const newState = () => mkdtemp(path.join(tmpdir(), "grok-cli-degrade-state-"));

async function run(args, stateDir) {
  const env = {
    ...process.env,
    HOME: testHome,
    USERPROFILE: testHome,
    GROK_STATE_DIR: stateDir,
    GROK_API_URL: endpoint,
    GROK_API_KEY: "stub-key",
    TAVILY_API_KEY: "",
    TAVILY_API_KEYS: "",
    TAVILY_PROXY_URL: "",
    FIRECRAWL_API_KEY: "",
    FIRECRAWL_API_KEYS: "",
    EXA_API_KEY: "",
    MCP_TAVILY_URL: "",
    FATHOM_API_URL: "",
    GROK_DEFAULT_EXTRA: "",
    GROK_DEADLINE_SECONDS: "",
    GROK_SEARCH_SOURCE: "",
  };
  try {
    const result = await execFileAsync("node", ["scripts/search.js", ...args], { cwd: process.cwd(), env });
    return { code: 0, out: JSON.parse(result.stdout) };
  } catch (error) {
    return { code: error.code, out: JSON.parse(error.stdout || "{}") };
  }
}

// --- 1. upstream 500: plain failure, then the transient cooldown holds -----------------------
const stateA = await newState();
mode = "500";
hits = 0;
const first = await run(["--no-extra", "stub query"], stateA);
assert.equal(first.code, 1);
assert.equal(first.out.error.code, "SEARCH_ERROR");
assert.match(first.out.error.message, /HTTP 500/);
const hitsAfterFirst = hits;
assert.ok(hitsAfterFirst > 0, "the failing call must actually reach the upstream");

const record = JSON.parse(await readFile(path.join(stateA, "grok-cooldown.json"), "utf8"));
assert.equal(record.reason, "stub_500");
const ttl = Date.parse(record.until) - Date.now();
assert.ok(ttl > 0, `cooldown must still be running, ttl=${ttl}`);
assert.ok(ttl <= 120_000, `a 5xx cooldown is transient (~60s), got ${ttl}ms`);

const second = await run(["--no-extra", "stub query"], stateA);
assert.equal(second.code, 1);
assert.equal(second.out.error.code, "GROK_UPSTREAM_COOLDOWN");
assert.equal(hits, hitsAfterFirst, "a cooled-down call must not reach the upstream again");
assert.match(second.out.error.message, /stub_500/, "the cooldown message carries the original reason");

// --- 2. text-only 200: the billed answer is kept, but never passed off as grounded ----------
mode = "textonly";
const ungrounded = await run(["--no-extra", "stub query"], await newState());
assert.equal(ungrounded.code, 0, JSON.stringify(ungrounded.out.error));
assert.equal(ungrounded.out.diagnostics.responses_native_search, false);
assert.equal(ungrounded.out.diagnostics.degraded, true);
assert.match(ungrounded.out.answer.text, /^> ⚠️ 未经搜索取证/);
assert.match(ungrounded.out.answer.text, /Stub answer from memory\./);
assert.ok(ungrounded.out.diagnostics.warnings.some((warning) => /未执行服务端搜索/.test(warning)));

// --- 3. truncated 200: the partial answer survives, and the truncation is reported ----------
mode = "incomplete";
const truncated = await run(["--no-extra", "stub query"], await newState());
assert.equal(truncated.code, 0, JSON.stringify(truncated.out.error));
assert.match(truncated.out.answer.text, /Stub partial answer/);
assert.equal(truncated.out.diagnostics.responses_status, "incomplete");
assert.equal(truncated.out.diagnostics.responses_incomplete_reason, "max_output_tokens");
assert.ok(truncated.out.diagnostics.warnings.some((warning) => /max_output_tokens/.test(warning)));

server.close();
console.log("cli-degrade.test.js: ok");
process.exit(0);
