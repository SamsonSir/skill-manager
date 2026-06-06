#!/usr/bin/env node
import { createHash } from "node:crypto";
import {
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  realpathSync,
  renameSync,
  statSync,
  symlinkSync,
  unlinkSync,
  writeFileSync
} from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, join, relative, resolve } from "node:path";

const args = new Set(process.argv.slice(2));
const apply = args.has("--apply");
const stamp = new Date().toISOString().replace(/[:.]/g, "-");

const sharedRoot = join(homedir(), "agent-skills");
const sharedDir = join(sharedRoot, "shared");
const backupDir = join(sharedRoot, "backups", `ensure-links-${stamp}`);
const resultPath = join(sharedRoot, "logs", `ensure-links-${stamp}.json`);

const sourceRoots = [
  { label: "agents", path: join(homedir(), ".agents", "skills"), priority: 0 },
  { label: "codex", path: join(homedir(), ".codex", "skills"), priority: 1 },
  { label: "vault-agents", path: join(homedir(), "Documents", "JokerSu-knowledge", ".agents", "skills"), priority: 2 },
  { label: "shared", path: sharedDir, priority: 3 }
];

const targetRoots = [
  { label: "agents", path: join(homedir(), ".agents", "skills") },
  { label: "claude", path: join(homedir(), ".claude", "skills") },
  {
    label: "vault-agents",
    path: join(homedir(), "Documents", "JokerSu-knowledge", ".agents", "skills"),
    existingOnly: true
  }
];

function sha256(text) {
  return createHash("sha256").update(text).digest("hex");
}

function parseName(text, fallback) {
  if (!text.startsWith("---")) return fallback;
  const end = text.indexOf("\n---", 3);
  if (end === -1) return fallback;
  const match = text.slice(3, end).match(/^name:\s*(.*)$/m);
  return match ? match[1].trim().replace(/^['"]|['"]$/g, "") : fallback;
}

function scan(root, out = [], active = new Set()) {
  if (!existsSync(root.path)) return out;
  let real;
  try {
    if (!statSync(root.path).isDirectory()) return out;
    real = realpathSync(root.path);
  } catch {
    return out;
  }
  if (active.has(real)) return out;
  active.add(real);

  const skillPath = join(root.path, "SKILL.md");
  if (existsSync(skillPath)) {
    const text = readFileSync(skillPath, "utf8");
    out.push({
      name: parseName(text, basename(root.path)),
      folderName: basename(root.path),
      root: root.label,
      rootPath: root.path,
      priority: root.priority,
      folderPath: root.path,
      realFolderPath: realpathSync(root.path),
      hash: sha256(text),
      isSymlink: lstatSync(root.path).isSymbolicLink()
    });
  }

  for (const entry of readdirSync(root.path, { withFileTypes: true })) {
    if (entry.name.startsWith(".") || entry.name === "node_modules" || entry.name === ".git") continue;
    if (entry.isDirectory() || entry.isSymbolicLink()) {
      scan({ ...root, path: join(root.path, entry.name) }, out, active);
    }
  }

  active.delete(real);
  return out;
}

function canonical(skills) {
  return [...skills].sort((a, b) => {
    return a.priority - b.priority || a.folderName.localeCompare(b.folderName);
  })[0];
}

function backupPath(targetRoot, linkPath) {
  return join(backupDir, targetRoot.label, relative(targetRoot.path, linkPath));
}

function ensureInsideHome(target) {
  const resolved = resolve(target);
  const home = resolve(homedir());
  if (!resolved.startsWith(`${home}/`)) {
    throw new Error(`Refusing to operate outside home: ${target}`);
  }
}

function linkEntry(targetRoot, skill) {
  const existingSameName = scan({ label: targetRoot.label, path: targetRoot.path, priority: 0 })
    .find((item) => item.name === skill.name && item.realFolderPath === skill.realFolderPath);
  if (existingSameName) {
    return {
      type: existingSameName.folderPath === join(targetRoot.path, skill.folderName) ? "already-linked" : "already-linked-nested",
      linkPath: existingSameName.folderPath,
      target: skill.realFolderPath,
      skill
    };
  }

  const linkPath = join(targetRoot.path, skill.folderName);
  ensureInsideHome(linkPath);
  ensureInsideHome(skill.realFolderPath);

  if (existsSync(linkPath)) {
    if (lstatSync(linkPath).isSymbolicLink()) {
      const currentTarget = realpathSync(linkPath);
      if (currentTarget === skill.realFolderPath) {
        return { type: "already-linked", linkPath, target: skill.realFolderPath, skill };
      }
      if (apply) unlinkSync(linkPath);
      return { type: "relink", linkPath, target: skill.realFolderPath, skill };
    }

    const target = backupPath(targetRoot, linkPath);
    ensureInsideHome(target);
    if (apply) {
      mkdirSync(dirname(target), { recursive: true });
      renameSync(linkPath, target);
    }
    return { type: "backup-and-link", linkPath, target: skill.realFolderPath, backup: target, skill };
  }

  if (targetRoot.existingOnly) {
    return { type: "skip-missing", linkPath, target: skill.realFolderPath, skill };
  }

  return { type: "link-missing", linkPath, target: skill.realFolderPath, skill };
}

const sourceSkills = sourceRoots.flatMap((root) => scan(root));
const byName = Map.groupBy(sourceSkills, (skill) => skill.name);
const canonicalSkills = Array.from(byName.values()).map(canonical);
const actions = [];

for (const targetRoot of targetRoots) {
  if (apply) mkdirSync(targetRoot.path, { recursive: true });
  for (const skill of canonicalSkills) {
    actions.push(linkEntry(targetRoot, skill));
  }
}

if (apply) {
  for (const action of actions) {
    if (action.type === "link-missing" || action.type === "relink" || action.type === "backup-and-link") {
      mkdirSync(dirname(action.linkPath), { recursive: true });
      if (!existsSync(action.linkPath)) symlinkSync(action.target, action.linkPath, "dir");
    }
  }
}

mkdirSync(dirname(resultPath), { recursive: true });
writeFileSync(
  resultPath,
  JSON.stringify(
    {
      generatedAt: new Date().toISOString(),
      mode: apply ? "apply" : "dry-run",
      backupDir,
      summary: {
        sourceSkills: sourceSkills.length,
        canonicalSkills: canonicalSkills.length,
        actions: actions.length,
        linkMissing: actions.filter((action) => action.type === "link-missing").length,
        relink: actions.filter((action) => action.type === "relink").length,
        backupAndLink: actions.filter((action) => action.type === "backup-and-link").length,
        alreadyLinked: actions.filter((action) => action.type === "already-linked").length,
        alreadyLinkedNested: actions.filter((action) => action.type === "already-linked-nested").length,
        skipMissing: actions.filter((action) => action.type === "skip-missing").length
      },
      actions
    },
    null,
    2
  ) + "\n",
  "utf8"
);

console.log(`Ensure links ${apply ? "applied" : "dry-run"}`);
console.log(`Result: ${resultPath}`);
console.log(
  JSON.stringify(
    {
      sourceSkills: sourceSkills.length,
      canonicalSkills: canonicalSkills.length,
      linkMissing: actions.filter((action) => action.type === "link-missing").length,
      relink: actions.filter((action) => action.type === "relink").length,
      backupAndLink: actions.filter((action) => action.type === "backup-and-link").length,
      alreadyLinked: actions.filter((action) => action.type === "already-linked").length,
      alreadyLinkedNested: actions.filter((action) => action.type === "already-linked-nested").length,
      skipMissing: actions.filter((action) => action.type === "skip-missing").length
    },
    null,
    2
  )
);
