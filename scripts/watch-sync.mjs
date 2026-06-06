#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { appendFileSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const nodePath = process.execPath;
const logPath = join(homedir(), "agent-skills", "logs", "watch-sync.log");

function log(message) {
  mkdirSync(dirname(logPath), { recursive: true });
  appendFileSync(logPath, `[${new Date().toISOString()}] ${message}\n`, "utf8");
  console.log(message);
}

function run(script) {
  const scriptPath = join(__dirname, script);
  log(`Running ${script}`);
  execFileSync(nodePath, [scriptPath, "--apply"], { stdio: "inherit" });
}

try {
  run("sync-new.mjs");
  run("ensure-agent-links.mjs");
  log("watch-sync complete");
} catch (error) {
  log(`watch-sync failed: ${error.message}`);
  process.exitCode = 1;
}
