#!/usr/bin/env node

import { createHash } from "node:crypto";
import { lstat, mkdir, readFile, readdir, realpath, stat, writeFile } from "node:fs/promises";
import { basename, dirname, join, normalize, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

type OwnershipKind = "user_authored" | "external" | "modified_external" | "unknown";
type Ownership = { kind: OwnershipKind; evidence: string };
type Provenance = Ownership & { source: "ownership_file" | "path" | "install_lock" | "unknown" };

type Entry = {
  discoveryPath: string;
  skillFile: string;
  canonicalFile: string;
  name: string | null;
  description: string | null;
  metadata: "frontmatter" | "absent_or_unreadable";
  sha256: string;
  mtimeMs: number;
  provenance: Provenance;
  enabled: "unknown";
  usage: "unknown";
};

type Alias = {
  path: string;
  status: "resolved" | "broken";
  target: string | null;
};

const LIMITS = [
  "Only explicit roots are inspected.",
  "Discovery is limited to direct children and children of a direct .system directory.",
  "SKILL.md bodies are not interpreted or executed; only simple YAML frontmatter name and description fields are extracted.",
  "Enabled state and usage are not inferred.",
  "Path provenance is heuristic; unclassified skills remain unknown.",
];
const HELP = "usage: skill-audit-lab inventory --root PATH [--root PATH ...] --output FILE [--ownership FILE]";

function usage(): never {
  throw new Error(HELP);
}

function parseArgs(argv: string[]) {
  if (argv.shift() !== "inventory") usage();
  const roots: string[] = [];
  let output: string | undefined;
  let ownership: string | undefined;
  while (argv.length) {
    const flag = argv.shift();
    const value = argv.shift();
    if (!value) usage();
    if (flag === "--root") roots.push(resolve(value));
    else if (flag === "--output") output = resolve(value);
    else if (flag === "--ownership") ownership = resolve(value);
    else usage();
  }
  if (!roots.length || !output) usage();
  return { roots: [...new Set(roots)].sort(), output, ownership };
}

function scalar(frontmatter: string, key: string): string | null {
  const match = frontmatter.match(new RegExp(`^${key}:\\s*(.+?)\\s*$`, "m"));
  if (!match) return null;
  const value = match[1].trim();
  if (/^[>|][+-]?$/.test(value)) return null;
  if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
    return value.slice(1, -1);
  }
  return value;
}

function metadata(bytes: Buffer) {
  const prefix = bytes.subarray(0, Math.min(bytes.length, 16_384)).toString("utf8");
  const match = prefix.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  if (!match) return { name: null, description: null, metadata: "absent_or_unreadable" as const };
  return { name: scalar(match[1], "name"), description: scalar(match[1], "description"), metadata: "frontmatter" as const };
}

async function loadOwnership(path?: string): Promise<Map<string, Ownership>> {
  if (!path) return new Map();
  const parsed = JSON.parse(await readFile(path, "utf8")) as Record<string, Ownership>;
  const valid = new Set<OwnershipKind>(["user_authored", "external", "modified_external", "unknown"]);
  const result = new Map<string, Ownership>();
  for (const [file, value] of Object.entries(parsed)) {
    if (!value || !valid.has(value.kind) || typeof value.evidence !== "string") {
      throw new Error(`invalid ownership entry for ${file}`);
    }
    result.set(resolve(file), value);
  }
  return result;
}

async function installLockMatches(root: string, candidates: Set<string>): Promise<boolean> {
  const lock = join(dirname(root), ".skill-lock.json");
  try {
    const parsed = JSON.parse(await readFile(lock, "utf8")) as { skills?: Record<string, Record<string, unknown>> };
    for (const value of Object.values(parsed.skills ?? {})) {
      for (const key of ["installPath", "installedPath", "path", "skillPath"]) {
        const candidate = value[key];
        if (typeof candidate === "string" && candidate.startsWith(sep) && candidates.has(resolve(candidate))) return true;
      }
    }
    return false;
  } catch {
    return false;
  }
}

async function classify(root: string, discoveryPath: string, canonicalFile: string, ownership: Map<string, Ownership>): Promise<Provenance> {
  const declared = ownership.get(canonicalFile);
  if (declared) return { ...declared, source: "ownership_file" };
  const paths = `${discoveryPath}${sep}${canonicalFile}`;
  if (paths.includes(`${sep}.codex${sep}plugins${sep}`)) {
    return { kind: "external", evidence: "path is inside the Codex plugin cache", source: "path" };
  }
  if (paths.includes(`${sep}.system${sep}`)) {
    return { kind: "external", evidence: "path is inside a managed .system skill directory", source: "path" };
  }
  const candidates = new Set([resolve(discoveryPath), resolve(dirname(canonicalFile)), resolve(canonicalFile)]);
  if (await installLockMatches(root, candidates)) {
    return { kind: "external", evidence: "an adjacent .skill-lock.json contains an exact path match", source: "install_lock" };
  }
  return { kind: "unknown", evidence: "no explicit ownership or safe provenance match", source: "unknown" };
}

type CoverageError = { root: string; error: string };

async function candidatePaths(root: string, errors: CoverageError[]): Promise<string[]> {
  const direct = await readdir(root, { withFileTypes: true });
  const candidates = direct.filter((item) => item.name !== ".system").map((item) => join(root, item.name));
  const system = direct.find((item) => item.name === ".system");
  if (system) {
    try {
      for (const item of await readdir(join(root, ".system"), { withFileTypes: true })) candidates.push(join(root, ".system", item.name));
    } catch (error) {
      errors.push({ root: join(root, ".system"), error: error instanceof Error ? error.message : String(error) });
    }
  }
  return candidates.sort();
}

async function inspectCandidate(root: string, path: string, ownership: Map<string, Ownership>, aliases: Alias[]): Promise<Entry | null> {
  const link = await lstat(path);
  if (link.isSymbolicLink()) {
    try {
      aliases.push({ path, status: "resolved", target: await realpath(path) });
    } catch {
      aliases.push({ path, status: "broken", target: null });
      return null;
    }
  }
  let canonicalFile: string;
  try {
    canonicalFile = await realpath(join(path, "SKILL.md"));
  } catch (error) {
    if (
      error &&
      typeof error === "object" &&
      "code" in error &&
      (error.code === "ENOENT" || error.code === "ENOTDIR")
    ) {
      return null;
    }
    throw error;
  }
  const [bytes, info] = await Promise.all([readFile(canonicalFile), stat(canonicalFile)]);
  const fields = metadata(bytes);
  return {
    discoveryPath: path,
    skillFile: join(path, "SKILL.md"),
    canonicalFile,
    ...fields,
    sha256: createHash("sha256").update(bytes).digest("hex"),
    mtimeMs: Math.trunc(info.mtimeMs),
    provenance: await classify(root, path, canonicalFile, ownership),
    enabled: "unknown",
    usage: "unknown",
  };
}

function grouped(entries: Entry[], key: (entry: Entry) => string): string[][] {
  const groups = new Map<string, Set<string>>();
  for (const entry of entries) {
    const values = groups.get(key(entry)) ?? new Set<string>();
    values.add(entry.discoveryPath);
    groups.set(key(entry), values);
  }
  return [...groups.values()].filter((paths) => paths.size > 1).map((paths) => [...paths].sort()).sort((a, b) => a[0].localeCompare(b[0]));
}

function identicalContentGroups(entries: Entry[]): string[][] {
  const groups = new Map<string, Set<string>>();
  for (const entry of entries) {
    const files = groups.get(entry.sha256) ?? new Set<string>();
    files.add(entry.canonicalFile);
    groups.set(entry.sha256, files);
  }
  return [...groups.values()].filter((files) => files.size > 1).map((files) => [...files].sort()).sort((a, b) => a[0].localeCompare(b[0]));
}

function isWithin(root: string, path: string): boolean {
  const child = relative(root, path);
  return child === "" || (!child.startsWith(`..${sep}`) && child !== "..");
}

async function canonicalProspectivePath(path: string): Promise<string> {
  let cursor = resolve(path);
  const suffix: string[] = [];
  while (true) {
    try {
      return join(await realpath(cursor), ...suffix);
    } catch {
      const parent = dirname(cursor);
      if (parent === cursor) return resolve(path);
      suffix.unshift(basename(cursor));
      cursor = parent;
    }
  }
}

export async function inventory(argv: string[]) {
  const args = parseArgs([...argv]);
  const [canonicalOutput, canonicalRoots] = await Promise.all([
    canonicalProspectivePath(args.output),
    Promise.all(args.roots.map(async (root) => realpath(root).catch(() => root))),
  ]);
  if (args.roots.some((root) => isWithin(root, args.output)) || canonicalRoots.some((root) => isWithin(root, canonicalOutput))) {
    throw new Error("--output must be outside every scanned root");
  }
  const ownership = await loadOwnership(args.ownership);
  const entries: Entry[] = [];
  const aliases: Alias[] = [];
  const errors: CoverageError[] = [];
  for (const root of args.roots) {
    try {
      for (const path of await candidatePaths(root, errors)) {
        try {
          const entry = await inspectCandidate(root, path, ownership, aliases);
          if (entry) entries.push(entry);
        } catch (error) {
          errors.push({ root: path, error: error instanceof Error ? error.message : String(error) });
        }
      }
    } catch (error) {
      errors.push({ root, error: error instanceof Error ? error.message : String(error) });
    }
  }
  entries.sort((a, b) => a.discoveryPath.localeCompare(b.discoveryPath));
  aliases.sort((a, b) => a.path.localeCompare(b.path));
  if (entries.some((entry) => isWithin(dirname(entry.canonicalFile), canonicalOutput))) {
    throw new Error("--output must be outside every discovered skill directory");
  }
  const sourceFingerprint = createHash("sha256")
    .update(JSON.stringify(entries.map(({ discoveryPath, canonicalFile, sha256, mtimeMs }) => ({ discoveryPath, canonicalFile, sha256, mtimeMs }))))
    .digest("hex");
  const report = {
    schemaVersion: "skill-audit-lab/v1",
    sourceFingerprint,
    coverage: { roots: args.roots, ownershipFile: args.ownership ?? null, limits: LIMITS, errors },
    entries,
    aliases,
    duplicateGroups: {
      canonicalTarget: grouped(entries, (entry) => entry.canonicalFile),
      identicalContent: identicalContentGroups(entries),
    },
  };
  await mkdir(dirname(args.output), { recursive: true });
  await writeFile(args.output, `${JSON.stringify(report, null, 2)}\n`);
  return report;
}

async function isMainModule(): Promise<boolean> {
  if (!process.argv[1]) return false;
  const argvPath = resolve(process.argv[1]);
  const modulePath = resolve(fileURLToPath(import.meta.url));
  const [canonicalArgv, canonicalModule] = await Promise.all([
    realpath(argvPath).catch(() => argvPath),
    realpath(modulePath).catch(() => modulePath),
  ]);
  return normalize(canonicalArgv) === normalize(canonicalModule);
}

if (await isMainModule()) {
  if (process.argv.slice(2).includes("--help") || process.argv.slice(2).includes("-h")) {
    console.log(HELP);
  } else inventory(process.argv.slice(2)).catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  });
}
