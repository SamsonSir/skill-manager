#!/usr/bin/env node
import { createHash } from "node:crypto";
import {
  existsSync,
  lstatSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  realpathSync,
  renameSync,
  statSync,
  writeFileSync
} from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(__dirname, "..");

const args = new Set(process.argv.slice(2));
const apply = args.has("--apply");
const allDuplicates = args.has("--all") || args.has("--all-duplicates");
const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
const backupRoot = valueAfter("--backup-root") || join(homedir(), "agent-skills", "backups", `prune-${timestamp}`);

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

function isDirectoryLike(path) {
  try {
    return statSync(path).isDirectory();
  } catch {
    return false;
  }
}

function scanRoot(root) {
  const skills = [];
  const activeRealpaths = new Set();

  function walk(dir) {
    if (!isDirectoryLike(dir)) return;
    let realpath;
    try {
      realpath = realpathSync(dir);
    } catch {
      return;
    }
    if (activeRealpaths.has(realpath)) return;
    activeRealpaths.add(realpath);

    const skillPath = join(dir, "SKILL.md");
    if (existsSync(skillPath)) {
      const text = readFileSync(skillPath, "utf8");
      const frontmatter = parseFrontmatter(text);
      const folderPath = dirname(skillPath);
      skills.push({
        name: frontmatter.name || basename(folderPath),
        description: frontmatter.description || "",
        folderName: basename(folderPath),
        root: root.label,
        rootPath: root.path,
        rootPriority: root.priority,
        folderPath,
        skillPath,
        relativeDir: relative(root.path, folderPath),
        hash: sha256(text),
        bytes: Buffer.byteLength(text),
        modifiedAt: statSync(skillPath).mtime.toISOString(),
        isSymlink: lstatSync(folderPath).isSymbolicLink()
      });
    }

    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      if (entry.name.startsWith(".") || entry.name === "node_modules") continue;
      const child = join(dir, entry.name);
      if (entry.isDirectory() || entry.isSymbolicLink()) {
        walk(child);
      }
    }

    activeRealpaths.delete(realpath);
  }

  walk(root.path);
  return skills;
}

function keepScore(skill) {
  let score = skill.rootPriority * 1000;
  if (skill.root === "agents" && skill.relativeDir.startsWith("superpowers/")) score -= 500;
  if (skill.isSymlink) score += 5;
  return score;
}

function publicSkill(skill) {
  return {
    name: skill.name,
    description: skill.description,
    root: skill.root,
    relativeDir: skill.relativeDir,
    folderPath: skill.folderPath,
    hash: skill.hash,
    bytes: skill.bytes,
    modifiedAt: skill.modifiedAt,
    isSymlink: skill.isSymlink
  };
}

function chooseCanonical(locations) {
  return [...locations].sort((a, b) => {
    return keepScore(a) - keepScore(b) || a.relativeDir.localeCompare(b.relativeDir);
  })[0];
}

function buildPlan(skills) {
  const byName = Map.groupBy(skills, (skill) => skill.name);
  const keep = new Set();
  const remove = new Set();
  const groups = [];

  for (const [name, locations] of byName.entries()) {
    if (locations.length === 1) {
      keep.add(locations[0].folderPath);
      continue;
    }

    const hashes = Array.from(new Set(locations.map((skill) => skill.hash)));
    const kept = [];
    const removed = [];

    if (allDuplicates || hashes.length === 1) {
      const canonical = chooseCanonical(locations);
      kept.push(canonical);
      keep.add(canonical.folderPath);
      for (const skill of locations) {
        if (skill.folderPath === canonical.folderPath) continue;
        removed.push(skill);
        remove.add(skill.folderPath);
      }
    } else {
      const byHash = Map.groupBy(locations, (skill) => skill.hash);
      for (const sameHashLocations of byHash.values()) {
        const canonical = chooseCanonical(sameHashLocations);
        kept.push(canonical);
        keep.add(canonical.folderPath);
        for (const skill of sameHashLocations) {
          if (skill.folderPath === canonical.folderPath) continue;
          removed.push(skill);
          remove.add(skill.folderPath);
        }
      }
    }

    groups.push({
      name,
      status: hashes.length === 1 ? "identical" : "different-content",
      hashes,
      keep: kept.map(publicSkill),
      remove: removed.map(publicSkill)
    });
  }

  const blocked = [];
  const actions = [];
  for (const group of groups) {
    for (const skill of group.remove) {
      const nestedKept = [...keep].find((keptPath) => {
        return keptPath !== skill.folderPath && keptPath.startsWith(`${skill.folderPath}/`) && !remove.has(keptPath);
      });
      if (nestedKept) {
        blocked.push({
          ...skill,
          reason: "folder contains a nested skill that is being kept",
          nestedKept
        });
        continue;
      }
      actions.push({
        type: "move-duplicate",
        name: group.name,
        source: skill.folderPath,
        target: join(backupRoot, skill.root, skill.relativeDir),
        skill
      });
    }
  }

  return {
    generatedAt: new Date().toISOString(),
    mode: apply ? "apply" : "dry-run",
    policy: allDuplicates ? "one-visible-entry-per-skill-name" : "dedupe-identical-content-per-skill-name",
    backupRoot,
    roots: roots.map(({ label, path }) => ({ label, path })),
    summary: {
      totalSkills: skills.length,
      uniqueNames: byName.size,
      duplicateNames: groups.length,
      differentContentDuplicateNames: groups.filter((group) => group.status === "different-content").length,
      keepEntries: groups.reduce((sum, group) => sum + group.keep.length, 0),
      removeEntries: actions.length,
      blockedEntries: blocked.length
    },
    groups,
    blocked,
    actions
  };
}

function ensureInsideHome(target) {
  const resolved = resolve(target);
  const home = resolve(homedir());
  if (!resolved.startsWith(`${home}/`)) {
    throw new Error(`Refusing to operate outside home directory: ${target}`);
  }
}

function execute(plan) {
  const results = [];
  for (const action of plan.actions) {
    ensureInsideHome(action.source);
    ensureInsideHome(action.target);
    mkdirSync(dirname(action.target), { recursive: true });
    if (existsSync(action.target)) {
      throw new Error(`Backup target already exists, refusing to overwrite: ${action.target}`);
    }
    renameSync(action.source, action.target);
    results.push({ ...action, result: "moved-to-backup" });
  }
  return results;
}

const skills = roots.flatMap(scanRoot);
const plan = buildPlan(skills);
const planPath = join(projectRoot, "data", "prune-duplicates-plan.json");
writeFileSync(planPath, JSON.stringify(plan, null, 2) + "\n", "utf8");

console.log(`${apply ? "Apply" : "Dry-run"} duplicate prune plan`);
console.log(`Plan: ${planPath}`);
console.log(`Backup root: ${backupRoot}`);
console.log(JSON.stringify(plan.summary, null, 2));

if (!apply) {
  console.log("No filesystem changes were made. Re-run with --apply to execute.");
  process.exit(0);
}

const results = execute(plan);
const resultPath = join(projectRoot, "data", "prune-duplicates-result.json");
writeFileSync(resultPath, JSON.stringify({ ...plan, results }, null, 2) + "\n", "utf8");
console.log(`Applied. Result: ${resultPath}`);
