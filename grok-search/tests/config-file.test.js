#!/usr/bin/env node
// A config file authored on Windows can carry a byte-order mark: PowerShell 5.1's
// `Set-Content -Encoding utf8` writes UTF-8 with BOM and `Out-File` writes UTF-16LE.
// JSON.parse rejects both, and the wrapper used to turn that into CONFIG_FILE_INVALID, so a
// correctly-authored config failed every command with a message about invalid JSON.
import assert from "node:assert/strict";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";

const home = await mkdtemp(path.join(tmpdir(), "grok-config-file-"));
process.env.HOME = home;
process.env.USERPROFILE = home;

const { loadConfigFile } = await import("../scripts/lib/config.js");

const configDir = path.join(home, ".config", "grok-search");
await mkdir(configDir, { recursive: true });
const configPath = path.join(configDir, "config.json");
const payload = { apiKey: "sk-test-value", grokModel: "grok-4.7", providerWeights: { exa: 0 } };

async function loadWith(bytes) {
  await writeFile(configPath, bytes);
  return loadConfigFile();
}

// No BOM: the ordinary case keeps working.
assert.deepEqual(await loadWith(Buffer.from(JSON.stringify(payload), "utf8")), payload);

// UTF-8 with BOM.
assert.deepEqual(await loadWith(Buffer.concat([Buffer.from([0xef, 0xbb, 0xbf]), Buffer.from(JSON.stringify(payload), "utf8")])), payload);

// UTF-16LE with BOM (PowerShell `Out-File`).
assert.deepEqual(await loadWith(Buffer.concat([Buffer.from([0xff, 0xfe]), Buffer.from(JSON.stringify(payload), "utf16le")])), payload);

// UTF-16BE with BOM: byte-swapped afterwards, so non-ASCII values must survive too.
const bePayload = { ...payload, note: "中文配置" };
const beBytes = Buffer.from(JSON.stringify(bePayload), "utf16le");
beBytes.swap16();
assert.deepEqual(await loadWith(Buffer.concat([Buffer.from([0xfe, 0xff]), beBytes])), bePayload);

// Genuinely broken JSON still fails, and still names the file and the code.
await writeFile(configPath, "{ bad json", "utf8");
await assert.rejects(loadConfigFile(), (error) => {
  assert.equal(error.code, "CONFIG_FILE_INVALID");
  assert.match(error.message, /不是有效 JSON/);
  return true;
});

// A missing file is "no overrides", not an error.
await rm(configPath);
assert.deepEqual(await loadConfigFile(), {});

await rm(home, { recursive: true, force: true });
console.log("config-file.test.js: ok");
