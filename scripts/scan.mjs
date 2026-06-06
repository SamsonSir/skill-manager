#!/usr/bin/env node
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import {
  existsSync,
  lstatSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  realpathSync,
  statSync,
  writeFileSync
} from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(__dirname, "..");

const roots = [
  { label: "agents", family: "agents", scope: "global", path: join(homedir(), ".agents", "skills") },
  { label: "claude", family: "claude", scope: "global", path: join(homedir(), ".claude", "skills") },
  { label: "codex", family: "codex", scope: "global", path: join(homedir(), ".codex", "skills") },
  {
    label: "vault-agents",
    family: "agents",
    scope: "JokerSu-knowledge",
    path: join(homedir(), "Documents", "JokerSu-knowledge", ".agents", "skills")
  }
];

const launchAgentLabel = "com.jokersu.skill-manager.sync";
const launchAgentPath = join(homedir(), "Library", "LaunchAgents", `${launchAgentLabel}.plist`);
const watchSyncLogPath = join(homedir(), "agent-skills", "logs", "watch-sync.log");

function sha256(text) {
  return createHash("sha256").update(text).digest("hex");
}

function parseFrontmatter(text) {
  if (!text.startsWith("---")) return { data: {}, error: "missing frontmatter" };
  const end = text.indexOf("\n---", 3);
  if (end === -1) return { data: {}, error: "unterminated frontmatter" };
  const raw = text.slice(3, end).trim();
  const data = {};
  for (const line of raw.split(/\r?\n/)) {
    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!match) continue;
    let value = match[2].trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    data[match[1]] = value;
  }
  return { data, error: null };
}

function findSkillFiles(root) {
  if (!existsSync(root)) return [];
  const files = [];
  const activeRealpaths = new Set();

  function walk(dir) {
    let realpath;
    try {
      if (!statSync(dir).isDirectory()) return;
      realpath = realpathSync(dir);
    } catch {
      return;
    }
    if (activeRealpaths.has(realpath)) return;
    activeRealpaths.add(realpath);

    const skillPath = join(dir, "SKILL.md");
    if (existsSync(skillPath)) files.push(skillPath);

    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.name.startsWith(".") || entry.name === "node_modules") continue;
      if (entry.isDirectory() || entry.isSymbolicLink()) {
        walk(join(dir, entry.name));
      }
    }

    activeRealpaths.delete(realpath);
  }

  walk(root);
  return files;
}

function collectBrokenSymlinks(root) {
  const broken = [];
  const activeRealpaths = new Set();

  function walk(dir) {
    if (!existsSync(dir)) return;
    let entries;
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }

    for (const entry of entries) {
      if (entry.name.startsWith(".") || entry.name === "node_modules") continue;
      const itemPath = join(dir, entry.name);
      let stats;
      try {
        stats = lstatSync(itemPath);
      } catch {
        continue;
      }

      if (stats.isSymbolicLink()) {
        if (!existsSync(itemPath)) {
          broken.push({
            path: itemPath,
            relativePath: relative(root, itemPath)
          });
          continue;
        }
      }

      let realpath;
      try {
        realpath = realpathSync(itemPath);
      } catch {
        continue;
      }
      if (activeRealpaths.has(realpath)) continue;

      try {
        if (statSync(itemPath).isDirectory()) {
          activeRealpaths.add(realpath);
          walk(itemPath);
          activeRealpaths.delete(realpath);
        }
      } catch {}
    }
  }

  walk(root);
  return broken;
}

function groupByName(items) {
  const byName = new Map();
  for (const item of items) {
    if (!byName.has(item.name)) byName.set(item.name, []);
    byName.get(item.name).push(item);
  }
  return byName;
}

function compareSkillSets(leftItems, rightItems) {
  const left = groupByName(leftItems);
  const right = groupByName(rightItems);
  const leftNames = new Set(left.keys());
  const rightNames = new Set(right.keys());
  const commonNames = Array.from(leftNames).filter((name) => rightNames.has(name)).sort();
  const leftOnly = Array.from(leftNames).filter((name) => !rightNames.has(name)).sort();
  const rightOnly = Array.from(rightNames).filter((name) => !leftNames.has(name)).sort();
  const mismatched = commonNames.filter((name) => {
    const leftHashes = Array.from(new Set(left.get(name).map((item) => item.hash))).sort();
    const rightHashes = Array.from(new Set(right.get(name).map((item) => item.hash))).sort();
    return leftHashes.length !== rightHashes.length || leftHashes.some((hash, index) => hash !== rightHashes[index]);
  });

  return {
    leftNames: leftNames.size,
    rightNames: rightNames.size,
    commonNames: commonNames.length,
    leftOnly,
    rightOnly,
    mismatched
  };
}

function watcherStatus() {
  const status = {
    label: launchAgentLabel,
    plistPath: launchAgentPath,
    installed: existsSync(launchAgentPath),
    loaded: false,
    watching: false,
    state: "not installed",
    runs: null,
    lastExitCode: null,
    lastLogLine: "",
    logPath: watchSyncLogPath
  };

  if (status.installed) {
    try {
      const output = execFileSync("launchctl", ["print", `gui/${process.getuid()}/${launchAgentLabel}`], {
        encoding: "utf8",
        stdio: ["ignore", "pipe", "ignore"]
      });
      status.loaded = true;
      status.watching = output.includes("watching = 1");
      status.state = output.match(/state = ([^\n]+)/)?.[1]?.trim() || "loaded";
      const runs = output.match(/runs = ([0-9]+)/)?.[1];
      const lastExitCode = output.match(/last exit code = ([0-9]+)/)?.[1];
      status.runs = runs ? Number(runs) : null;
      status.lastExitCode = lastExitCode ? Number(lastExitCode) : null;
    } catch {
      status.state = "installed but not loaded";
    }
  }

  if (existsSync(watchSyncLogPath)) {
    const lines = readFileSync(watchSyncLogPath, "utf8").trim().split(/\r?\n/).filter(Boolean);
    status.lastLogLine = lines.at(-1) || "";
  }

  return status;
}

function scanRoot(root) {
  const files = findSkillFiles(root.path);
  const skills = files.map((skillPath) => {
    const text = readFileSync(skillPath, "utf8");
    const parsed = parseFrontmatter(text);
    const folder = dirname(skillPath);
    const name = parsed.data.name || folder.split("/").pop();
    const stats = statSync(skillPath);
    const realFolderPath = realpathSync(folder);
    return {
      name,
      folderName: folder.split("/").pop(),
      description: parsed.data.description || "",
      root: root.label,
      family: root.family || root.label,
      scope: root.scope || "global",
      rootPath: root.path,
      path: skillPath,
      relativePath: relative(root.path, skillPath),
      realFolderPath,
      hash: sha256(text),
      bytes: Buffer.byteLength(text),
      modifiedAt: stats.mtime.toISOString(),
      isSymlink: lstatSync(folder).isSymbolicLink(),
      frontmatterError: parsed.error
    };
  });

  return {
    root: {
      ...root,
      total: skills.length,
      symlinks: skills.filter((skill) => skill.isSymlink).length
    },
    skills
  };
}

const scanned = roots.map(scanRoot);
const skills = scanned.flatMap((item) => item.skills);
const byName = groupByName(skills);

const groups = Array.from(byName.entries())
  .map(([name, locations]) => {
    const hashes = Array.from(new Set(locations.map((item) => item.hash)));
    const realFolderPaths = Array.from(new Set(locations.map((item) => item.realFolderPath)));
    const status =
      locations.length === 1
        ? "unique"
        : realFolderPaths.length === 1
          ? "linked"
          : hashes.length === 1
            ? "identical"
            : "conflict";
    return {
      name,
      status,
      hashes,
      realFolderPaths,
      needsAction: status === "conflict" || status === "identical",
      locations: locations.map((item) => ({
        root: item.root,
        family: item.family,
        scope: item.scope,
        path: item.path,
        relativePath: item.relativePath,
        realFolderPath: item.realFolderPath,
        hash: item.hash,
        modifiedAt: item.modifiedAt,
        bytes: item.bytes,
        isSymlink: item.isSymlink,
        description: item.description
      }))
    };
  })
  .sort((a, b) => {
    const order = { conflict: 0, identical: 1, linked: 2, unique: 3 };
    return order[a.status] - order[b.status] || a.name.localeCompare(b.name);
  });

const summary = {
  totalFiles: skills.length,
  uniqueNames: groups.length,
  duplicateNames: groups.filter((group) => group.locations.length > 1).length,
  linkedNames: groups.filter((group) => group.status === "linked").length,
  physicalDuplicateNames: groups.filter((group) => group.locations.length > 1 && group.status !== "linked").length,
  identicalNames: groups.filter((group) => group.status === "identical").length,
  conflictNames: groups.filter((group) => group.status === "conflict").length,
  uniqueOnlyNames: groups.filter((group) => group.status === "unique").length
};

const brokenSymlinks = roots.flatMap((root) =>
  collectBrokenSymlinks(root.path).map((item) => ({
    root: root.label,
    rootPath: root.path,
    ...item
  }))
);
const codexSkills = skills.filter((skill) => skill.family === "agents" || skill.family === "codex");
const claudeSkills = skills.filter((skill) => skill.family === "claude");
const codexClaudeSync = compareSkillSets(codexSkills, claudeSkills);
const watcher = watcherStatus();
const actionItems = [
  ...groups
    .filter((group) => group.needsAction)
    .map((group) => ({
      type: group.status,
      title: group.name,
      detail: `${group.locations.length} entries, ${group.hashes.length} versions`
    })),
  ...brokenSymlinks.map((item) => ({
    type: "broken-symlink",
    title: item.relativePath,
    detail: item.path
  })),
  ...codexClaudeSync.leftOnly.map((name) => ({
    type: "codex-only",
    title: name,
    detail: "Visible to Codex, missing from Claude"
  })),
  ...codexClaudeSync.rightOnly.map((name) => ({
    type: "claude-only",
    title: name,
    detail: "Visible to Claude, missing from Codex"
  })),
  ...codexClaudeSync.mismatched.map((name) => ({
    type: "mismatch",
    title: name,
    detail: "Codex and Claude content hashes differ"
  }))
];
const healthChecks = [
  { id: "sync", label: "Codex / Claude 同步", ok: codexClaudeSync.leftOnly.length === 0 && codexClaudeSync.rightOnly.length === 0 && codexClaudeSync.mismatched.length === 0 },
  { id: "conflicts", label: "同名冲突", ok: summary.conflictNames === 0 },
  { id: "physical-duplicates", label: "实体重复", ok: summary.physicalDuplicateNames === 0 },
  { id: "broken-symlinks", label: "坏软链接", ok: brokenSymlinks.length === 0 },
  { id: "watcher", label: "自动同步 watcher", ok: watcher.installed && watcher.loaded && watcher.watching && watcher.lastExitCode === 0 }
];
const healthStatus = healthChecks.every((check) => check.ok)
  ? "healthy"
  : healthChecks.some((check) => check.id === "sync" && !check.ok) || summary.conflictNames > 0 || brokenSymlinks.length > 0
    ? "attention"
    : "warning";

const report = {
  generatedAt: new Date().toISOString(),
  roots: scanned.map((item) => item.root),
  summary,
  health: {
    status: healthStatus,
    checks: healthChecks,
    actionItems,
    actionCount: actionItems.length,
    brokenSymlinks,
    watcher,
    codexClaudeSync
  },
  groups
};

const outputPath = join(projectRoot, "data", "report.js");
mkdirSync(dirname(outputPath), { recursive: true });
writeFileSync(
  outputPath,
  `window.SKILL_MANAGER_REPORT = ${JSON.stringify(report, null, 2)};\n`,
  "utf8"
);

console.log(`Wrote ${outputPath}`);
console.log(`Skills: ${summary.totalFiles}, unique names: ${summary.uniqueNames}, conflicts: ${summary.conflictNames}`);
