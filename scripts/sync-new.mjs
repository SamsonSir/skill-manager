#!/usr/bin/env node
import { createHash } from "node:crypto";
import {
  appendFileSync,
  cpSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  renameSync,
  statSync,
  symlinkSync,
  writeFileSync
} from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, join, resolve } from "node:path";

const args = new Set(process.argv.slice(2));
const apply = args.has("--apply");
const now = new Date();
const stamp = now.toISOString().replace(/[:.]/g, "-");

const sharedRoot = valueAfter("--shared-root") || join(homedir(), "agent-skills");
const sharedDir = join(sharedRoot, "shared");
const overridesDir = join(sharedRoot, "overrides");
const backupDir = join(sharedRoot, "backups", `sync-${stamp}`);
const logPath = join(sharedRoot, "logs", "sync-new.log");

const roots = [
  { label: "agents", path: join(homedir(), ".agents", "skills"), priority: 0 },
  { label: "claude", path: join(homedir(), ".claude", "skills"), priority: 1 },
  { label: "codex", path: join(homedir(), ".codex", "skills"), priority: 2 }
];

function valueAfter(flag) {
  const index = process.argv.indexOf(flag);
  return index >= 0 ? process.argv[index + 1] : null;
}

function log(message) {
  const line = `[${new Date().toISOString()}] ${message}\n`;
  mkdirSync(dirname(logPath), { recursive: true });
  appendFileSync(logPath, line, "utf8");
  console.log(message);
}

function sha256(text) {
  return createHash("sha256").update(text).digest("hex");
}

function parseFrontmatter(text) {
  if (!text.startsWith("---")) return {};
  const end = text.indexOf("\n---", 3);
  if (end === -1) return {};
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
  return data;
}

function skillInfo(root, folderPath) {
  const skillPath = join(folderPath, "SKILL.md");
  if (!existsSync(skillPath)) return null;
  const text = readFileSync(skillPath, "utf8");
  const frontmatter = parseFrontmatter(text);
  return {
    name: frontmatter.name || basename(folderPath),
    folderName: basename(folderPath),
    root: root.label,
    folderPath,
    skillPath,
    hash: sha256(text),
    bytes: Buffer.byteLength(text),
    modifiedAt: statSync(skillPath).mtime.toISOString(),
    isSymlink: lstatSync(folderPath).isSymbolicLink()
  };
}

function listRootSkills(root) {
  if (!existsSync(root.path)) return [];
  return readdirSync(root.path, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() || entry.isSymbolicLink())
    .map((entry) => skillInfo(root, join(root.path, entry.name)))
    .filter(Boolean);
}

function listSharedSkills() {
  if (!existsSync(sharedDir)) return [];
  const root = { label: "shared", path: sharedDir };
  return readdirSync(sharedDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() || entry.isSymbolicLink())
    .map((entry) => skillInfo(root, join(sharedDir, entry.name)))
    .filter(Boolean);
}

function ensureInsideHome(path) {
  const resolved = resolve(path);
  const home = resolve(homedir());
  if (!resolved.startsWith(home + "/")) {
    throw new Error(`Refusing to operate outside home: ${path}`);
  }
}

function copyDir(source, target) {
  ensureInsideHome(target);
  mkdirSync(dirname(target), { recursive: true });
  cpSync(source, target, { recursive: true, dereference: true, preserveTimestamps: true });
}

function replaceWithSymlink(source, target, backup) {
  ensureInsideHome(source);
  ensureInsideHome(target);
  ensureInsideHome(backup);
  if (lstatSync(source).isSymbolicLink()) return "already-symlink";
  mkdirSync(dirname(backup), { recursive: true });
  renameSync(source, backup);
  symlinkSync(target, source, "dir");
  return "linked";
}

function buildPlan() {
  if (!existsSync(sharedDir)) {
    return {
      ready: false,
      reason: `Shared directory not found: ${sharedDir}. Run apply.mjs --apply once before enabling automatic sync.`,
      actions: []
    };
  }

  const shared = listSharedSkills();
  const sharedByFolder = new Map(shared.map((skill) => [skill.folderName, skill]));
  const sharedByName = Map.groupBy(shared, (skill) => skill.name);
  const actions = [];

  for (const root of roots) {
    for (const skill of listRootSkills(root)) {
      if (skill.isSymlink) continue;

      const byFolder = sharedByFolder.get(skill.folderName);
      const sameName = sharedByName.get(skill.name) || [];
      const exact = byFolder || sameName.find((item) => item.hash === skill.hash);
      const conflict = sameName.find((item) => item.hash !== skill.hash);

      if (exact && exact.hash === skill.hash) {
        actions.push({
          type: "link-existing",
          skill,
          target: exact.folderPath,
          backup: join(backupDir, root.label, skill.folderName)
        });
        continue;
      }

      if (conflict || (byFolder && byFolder.hash !== skill.hash)) {
        actions.push({
          type: "copy-conflict",
          skill,
          target: join(overridesDir, root.label, `${skill.folderName}-${stamp}`),
          reason: "shared has same skill name or folder with different content"
        });
        continue;
      }

      const target = join(sharedDir, skill.folderName);
      actions.push({
        type: "copy-and-link-new",
        skill,
        target,
        backup: join(backupDir, root.label, skill.folderName)
      });
    }
  }

  return { ready: true, actions };
}

function execute(plan) {
  const results = [];
  for (const action of plan.actions) {
    if (action.type === "copy-conflict") {
      if (apply) copyDir(action.skill.folderPath, action.target);
      results.push({ ...action, result: apply ? "copied-to-overrides" : "dry-run" });
      continue;
    }

    if (action.type === "copy-and-link-new") {
      if (apply) {
        copyDir(action.skill.folderPath, action.target);
        replaceWithSymlink(action.skill.folderPath, action.target, action.backup);
      }
      results.push({ ...action, result: apply ? "copied-and-linked" : "dry-run" });
      continue;
    }

    if (action.type === "link-existing") {
      if (apply) replaceWithSymlink(action.skill.folderPath, action.target, action.backup);
      results.push({ ...action, result: apply ? "linked-existing" : "dry-run" });
    }
  }
  return results;
}

const plan = buildPlan();
const planPath = join(sharedRoot, "logs", `sync-plan-${stamp}.json`);
mkdirSync(dirname(planPath), { recursive: true });
writeFileSync(planPath, JSON.stringify(plan, null, 2) + "\n", "utf8");

if (!plan.ready) {
  log(`Not ready: ${plan.reason}`);
  process.exit(0);
}

const results = execute(plan);
const summary = {
  mode: apply ? "apply" : "dry-run",
  actions: results.length,
  copyAndLinkNew: results.filter((item) => item.type === "copy-and-link-new").length,
  linkExisting: results.filter((item) => item.type === "link-existing").length,
  copyConflict: results.filter((item) => item.type === "copy-conflict").length,
  planPath
};

log(JSON.stringify(summary));
