import { afterEach, describe, expect, test } from "bun:test";
import { mkdtemp, mkdir, readFile, realpath, rm, symlink, utimes, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";
import { inventory } from "../src/cli";

const created: string[] = [];
afterEach(async () => Promise.all(created.splice(0).map((path) => rm(path, { recursive: true, force: true }))));

async function fixture() {
  const base = await mkdtemp(join(tmpdir(), "skill-audit-"));
  created.push(base);
  const root = join(base, "skills");
  await mkdir(root);
  const add = async (name: string, body: string, nested = false) => {
    const directory = nested ? join(root, ".system", name) : join(root, name);
    await mkdir(directory, { recursive: true });
    const file = join(directory, "SKILL.md");
    await writeFile(file, body);
    await utimes(file, new Date(1_700_000_000_000), new Date(1_700_000_000_000));
    return { directory, file };
  };
  return { base, root, add };
}

describe("inventory", () => {
  test("reports aliases, duplicate kinds, provenance, unknown state, and a stable fingerprint", async () => {
    const f = await fixture();
    const one = await f.add("one", "---\nname: shared\ndescription: First\n---\nDo not interpret me.\n");
    const copy = await f.add("copy", "---\nname: shared\ndescription: First\n---\nDo not interpret me.\n");
    await f.add("changed-name", "---\nname: shared\ndescription: Different\n---\nOther body.\n");
    const system = await f.add("managed", "---\nname: managed\n---\nBody.\n", true);
    await symlink(one.directory, join(f.root, "alias"));
    await symlink(join(f.base, "missing"), join(f.root, "broken"));
    const ownershipFile = join(f.base, "ownership.json");
    await writeFile(ownershipFile, JSON.stringify({ [await realpath(copy.file)]: { kind: "user_authored", evidence: "fixture declaration" } }));
    const output1 = join(f.base, "one.json");
    const output2 = join(f.base, "two.json");
    const first = await inventory(["inventory", "--root", f.root, "--output", output1, "--ownership", ownershipFile]);
    const second = await inventory(["inventory", "--root", f.root, "--output", output2, "--ownership", ownershipFile]);

    expect(first.sourceFingerprint).toBe(second.sourceFingerprint);
    expect(first.aliases).toContainEqual({ path: join(f.root, "broken"), status: "broken", target: null });
    expect(first.duplicateGroups.canonicalTarget).toContainEqual([join(f.root, "alias"), one.directory].sort());
    expect(first.duplicateGroups.identicalContent).toContainEqual([await realpath(copy.file), await realpath(one.file)].sort());
    expect(first.entries.find((entry) => entry.discoveryPath === copy.directory)?.provenance.kind).toBe("user_authored");
    const canonicalSystemFile = await realpath(system.file);
    expect(first.entries.find((entry) => entry.canonicalFile === canonicalSystemFile)?.provenance.kind).toBe("external");
    expect(first.entries.find((entry) => entry.discoveryPath === one.directory)?.provenance.kind).toBe("unknown");
    expect(first.entries.every((entry) => entry.enabled === "unknown" && entry.usage === "unknown")).toBe(true);
    expect(JSON.parse(await readFile(output1, "utf8")).schemaVersion).toBe("skill-audit-lab/v1");
  });

  test("uses an exact install-lock path match without treating every entry as external", async () => {
    const f = await fixture();
    const installed = await f.add("installed", "---\nname: installed\n---\nBody.\n");
    await f.add("other", "---\nname: other\n---\nBody.\n");
    await writeFile(join(f.base, ".skill-lock.json"), JSON.stringify({ skills: { installed: { skillPath: installed.directory } } }));
    const report = await inventory(["inventory", "--root", f.root, "--output", join(f.base, "report.json")]);
    expect(report.entries.find((entry) => entry.discoveryPath === installed.directory)?.provenance.source).toBe("install_lock");
    expect(report.entries.find((entry) => entry.discoveryPath.endsWith("other"))?.provenance.kind).toBe("unknown");
  });

  test("refuses to write a report into a scanned source root", async () => {
    const f = await fixture();
    await f.add("one", "---\nname: one\n---\nBody.\n");
    await expect(inventory(["inventory", "--root", f.root, "--output", join(f.root, "report.json")])).rejects.toThrow(
      "--output must be outside every scanned root",
    );
  });

  test("refuses an output path that enters a scanned root through a symlink", async () => {
    const f = await fixture();
    await f.add("one", "---\nname: one\n---\nBody.\n");
    const alias = join(f.base, "root-alias");
    await symlink(f.root, alias);
    await expect(inventory(["inventory", "--root", f.root, "--output", join(alias, "report.json")])).rejects.toThrow(
      "--output must be outside every scanned root",
    );
  });

  test("refuses to overwrite a canonical skill reached through an alias", async () => {
    const f = await fixture();
    const external = join(f.base, "external-skill");
    await mkdir(external);
    const externalFile = join(external, "SKILL.md");
    await writeFile(externalFile, "---\nname: external\n---\nBody.\n");
    await symlink(external, join(f.root, "external"));
    await expect(inventory(["inventory", "--root", f.root, "--output", externalFile])).rejects.toThrow(
      "--output must be outside every discovered skill directory",
    );
  });

  test("reports unexpected SKILL.md resolution failures in coverage", async () => {
    const f = await fixture();
    const loop = join(f.root, "loop");
    await mkdir(loop);
    await symlink("SKILL.md", join(loop, "SKILL.md"));
    const report = await inventory(["inventory", "--root", f.root, "--output", join(f.base, "report.json")]);
    expect(report.coverage.errors).toHaveLength(1);
    expect(report.coverage.errors[0]?.root).toBe(loop);
    expect(report.coverage.errors[0]?.error).toContain("too many symbolic links");
  });

  test("runs the built CLI through a symlink and writes the requested report", async () => {
    const f = await fixture();
    await f.add("one", "---\nname: one\n---\nBody.\n");
    const built = join(f.base, "dist", "cli.js");
    await mkdir(join(f.base, "dist"));
    const source = fileURLToPath(new URL("../src/cli.ts", import.meta.url));
    const build = Bun.spawn([process.execPath, "build", source, "--target=node", `--outfile=${built}`], {
      stdout: "pipe",
      stderr: "pipe",
    });
    const buildError = await new Response(build.stderr).text();
    expect(await build.exited, buildError).toBe(0);
    const alias = join(f.base, "skill-audit-lab");
    await symlink(built, alias);
    const output = join(f.base, "report.json");
    const run = Bun.spawn(["node", alias, "inventory", "--root", f.root, "--output", output], {
      stdout: "pipe",
      stderr: "pipe",
    });
    const runError = await new Response(run.stderr).text();
    expect(await run.exited, runError).toBe(0);
    expect(JSON.parse(await readFile(output, "utf8")).entries).toHaveLength(1);
  });
});
