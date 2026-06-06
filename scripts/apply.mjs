#!/usr/bin/env node
import { createHash } from "node:crypto";
import {
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
import { basename, dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(__dirname, "..");

const args = new Set(process.argv.slice(2));
const apply = args.has("--apply");
const dryRun = !apply || args.has("--dry-run");
const duplicatesOnly = args.has("--duplicates-only");
const timestamp = new Date().toISOString().replace(/[:.]/g, "-");

const options = {
  sharedRoot: valueAfter("--shared-root") || join(homedir(), "agent-skills"),
  backupRoot: valueAfter("--backup-root") || join(homedir(), "agent-skills", "backups", timestamp)
};

const roots = [
  { label: "agents", path: join(homedir(), ".agents", "skills"), priority: 0 },
  { label: "claude", path: join(homedir(), ".claude", "skills"), priority: 1 },
  { label: "codex", path: join(homedir(), ".codex", "skills"), priority: 2 }
];

function valueAfter(flag) {
  const index = process.argv.indexOf(flag);
  return index >= 0 ? process.argv[index + 1] : null;
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

function findSkillFiles(root) {
  if (!existsSync(root.path)) return [];
  return readdirSync(root.path, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() || entry.isSymbolicLink())
    .map((entry) => join(root.path, entry.name, "SKILL.md"))
    .filter((skillPath) => existsSync(skillPath));
}

function scan() {
  const skills = [];
  for (const root of roots) {
    for (const skillPath of findSkillFiles(root)) {
      const text = readFileSync(skillPath, "utf8");
      const folderPath = dirname(skillPath);
      const frontmatter = parseFrontmatter(text);
      skills.push({
        name: frontmatter.name || basename(folderPath),
        folderName: basename(folderPath),
        root: root.label,
        rootPath: root.path,
        rootPriority: root.priority,
        folderPath,
        skillPath,
        relativePath: relative(root.path, skillPath),
        hash: sha256(text),
        bytes: Buffer.byteLength(text),
        modifiedAt: statSync(skillPath).mtime.toISOString(),
        isSymlink: lstatSync(folderPath).isSymbolicLink()
      });
    }
  }
  return skills;
}

function buildPlan(skills) {
  const groups = Map.groupBy(skills, (skill) => skill.name);
  const sharedDir = join(options.sharedRoot, "shared");
  const overridesDir = join(options.sharedRoot, "overrides");
  const actions = [];
  const conflicts = [];

  for (const [name, locations] of groups.entries()) {
    const hashes = Array.from(new Set(locations.map((skill) => skill.hash)));
    const sorted = [...locations].sort((a, b) => a.rootPriority - b.rootPriority || a.folderName.localeCompare(b.folderName));
    const canonical = sorted[0];

    if (duplicatesOnly && locations.length < 2) {
      continue;
    }

    if (hashes.length > 1) {
      conflicts.push({
        name,
        reason: "same skill name has different content hashes",
        locations: sorted.map(toPublicSkill)
      });
      if (duplicatesOnly) {
        continue;
      }
      for (const skill of sorted) {
        actions.push({
          type: "copy-conflict-version",
          name,
          source: skill.folderPath,
          target: join(overridesDir, skill.root, skill.folderName),
          skill: toPublicSkill(skill)
        });
      }
      continue;
    }

    const target = join(sharedDir, canonical.folderName);
    actions.push({
      type: "copy-shared",
      name,
      source: canonical.folderPath,
      target,
      skill: toPublicSkill(canonical)
    });

    for (const skill of sorted) {
      actions.push({
        type: "link-original",
        name,
        source: skill.folderPath,
        target,
        backup: join(options.backupRoot, skill.root, skill.folderName),
        skill: toPublicSkill(skill)
      });
    }
  }

  return {
    generatedAt: new Date().toISOString(),
    mode: apply ? "apply" : "dry-run",
    scope: duplicatesOnly ? "duplicates-only" : "all-non-conflict-skills",
    sharedRoot: options.sharedRoot,
    backupRoot: options.backupRoot,
    roots: roots.map(({ label, path }) => ({ label, path })),
    summary: {
      totalSkills: skills.length,
      uniqueNames: groups.size,
      conflicts: conflicts.length,
      copyShared: actions.filter((action) => action.type === "copy-shared").length,
      linkOriginal: actions.filter((action) => action.type === "link-original").length,
      copyConflictVersion: actions.filter((action) => action.type === "copy-conflict-version").length
    },
    conflicts,
    actions
  };
}

function toPublicSkill(skill) {
  return {
    name: skill.name,
    root: skill.root,
    folderName: skill.folderName,
    folderPath: skill.folderPath,
    relativePath: skill.relativePath,
    hash: skill.hash,
    bytes: skill.bytes,
    modifiedAt: skill.modifiedAt,
    isSymlink: skill.isSymlink
  };
}

function ensureInsideRoot(target) {
  const resolved = resolve(target);
  const home = resolve(homedir());
  if (!resolved.startsWith(home + "/")) {
    throw new Error(`Refusing to operate outside home directory: ${target}`);
  }
}

function copyDir(source, target) {
  ensureInsideRoot(target);
  if (existsSync(target)) return "exists";
  mkdirSync(dirname(target), { recursive: true });
  cpSync(source, target, { recursive: true, dereference: true, preserveTimestamps: true });
  return "copied";
}

function replaceWithSymlink(source, target, backup) {
  ensureInsideRoot(source);
  ensureInsideRoot(target);
  ensureInsideRoot(backup);

  if (lstatSync(source).isSymbolicLink()) {
    return "already-symlink";
  }

  mkdirSync(dirname(backup), { recursive: true });
  if (!existsSync(backup)) {
    renameSync(source, backup);
  } else {
    throw new Error(`Backup already exists, refusing to overwrite: ${backup}`);
  }

  symlinkSync(target, source, "dir");
  return "linked";
}

function execute(plan) {
  const results = [];
  for (const action of plan.actions) {
    if (action.type === "copy-shared" || action.type === "copy-conflict-version") {
      results.push({ ...action, result: copyDir(action.source, action.target) });
      continue;
    }
    if (action.type === "link-original") {
      results.push({ ...action, result: replaceWithSymlink(action.source, action.target, action.backup) });
    }
  }
  return results;
}

function writePlan(plan) {
  const planPath = join(projectRoot, "data", "migration-plan.json");
  writeFileSync(planPath, JSON.stringify(plan, null, 2) + "\n", "utf8");
  return planPath;
}

const skills = scan();
const plan = buildPlan(skills);
const planPath = writePlan(plan);

console.log(`${apply ? "Apply" : "Dry-run"} migration plan`);
console.log(`Plan: ${planPath}`);
console.log(`Shared root: ${plan.sharedRoot}`);
console.log(`Backup root: ${plan.backupRoot}`);
console.log(JSON.stringify(plan.summary, null, 2));

if (dryRun) {
  console.log("No filesystem changes were made. Re-run with --apply to execute.");
  process.exit(0);
}

const results = execute(plan);
const resultPath = join(projectRoot, "data", "migration-result.json");
writeFileSync(resultPath, JSON.stringify({ ...plan, results }, null, 2) + "\n", "utf8");
console.log(`Applied. Result: ${resultPath}`);
