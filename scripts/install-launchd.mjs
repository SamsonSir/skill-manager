#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const scriptPath = join(__dirname, "watch-sync.mjs");
const nodePath = process.execPath;
const label = "com.jokersu.skill-manager.sync";
const plistPath = join(homedir(), "Library", "LaunchAgents", `${label}.plist`);
const logDir = join(homedir(), "agent-skills", "logs");

const args = new Set(process.argv.slice(2));
const install = args.has("--install");
const uninstall = args.has("--uninstall");
const printOnly = args.has("--print") || (!install && !uninstall);

const watchedPaths = [
  join(homedir(), "agent-skills", "shared"),
  join(homedir(), ".agents", "skills"),
  join(homedir(), ".claude", "skills"),
  join(homedir(), ".codex", "skills"),
  join(homedir(), "Documents", "JokerSu-knowledge", ".agents", "skills")
];

const plist = `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${label}</string>
  <key>ProgramArguments</key>
  <array>
    <string>${nodePath}</string>
    <string>${scriptPath}</string>
    <string>--apply</string>
  </array>
  <key>WatchPaths</key>
  <array>
${watchedPaths.map((path) => `    <string>${path}</string>`).join("\n")}
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${join(logDir, "launchd.out.log")}</string>
  <key>StandardErrorPath</key>
  <string>${join(logDir, "launchd.err.log")}</string>
</dict>
</plist>
`;

function unloadIfLoaded() {
  try {
    execFileSync("launchctl", ["bootout", `gui/${process.getuid()}`, plistPath], { stdio: "ignore" });
  } catch {}
}

if (printOnly) {
  console.log(plist);
  console.log(`\nInstall with: node tools/skill-manager/scripts/install-launchd.mjs --install`);
  console.log(`Uninstall with: node tools/skill-manager/scripts/install-launchd.mjs --uninstall`);
  process.exit(0);
}

if (uninstall) {
  unloadIfLoaded();
  console.log(`Unloaded ${label}. Remove manually if desired: ${plistPath}`);
  process.exit(0);
}

if (install) {
  mkdirSync(dirname(plistPath), { recursive: true });
  mkdirSync(logDir, { recursive: true });
  writeFileSync(plistPath, plist, "utf8");
  unloadIfLoaded();
  execFileSync("launchctl", ["bootstrap", `gui/${process.getuid()}`, plistPath], { stdio: "inherit" });
  execFileSync("launchctl", ["enable", `gui/${process.getuid()}/${label}`], { stdio: "inherit" });
  console.log(`Installed and loaded ${plistPath}`);
  console.log(`Logs: ${logDir}`);
}
