from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "discover.py"


class DiscoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.home = self.base / "home"
        self.state = self.base / "state"
        self.home.mkdir()
        self.state.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_discovery(
        self, *roots: Path, extra_environment: dict[str, str] | None = None
    ) -> dict[str, object]:
        output = self.base / "result.json"
        environment = os.environ.copy()
        environment.update(
            HOME=str(self.home),
            XDG_STATE_HOME=str(self.state),
            CODEX_HOME=str(self.home / ".codex"),
            CLAUDE_CONFIG_DIR=str(self.home / ".claude"),
        )
        if extra_environment:
            environment.update(extra_environment)
        subprocess.run(
            [sys.executable, str(SCRIPT), *(str(root) for root in roots), "--output", str(output)],
            check=True,
            env=environment,
            capture_output=True,
            text=True,
        )
        return json.loads(output.read_text(encoding="utf-8"))

    def write(self, path: Path, content: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_follows_spaced_links_imports_obsidian_and_cycles(self) -> None:
        root = self.base / "project"
        agents = self.write(
            root / "AGENTS.md",
            "[guide](<docs/Guide With Spaces.md>)\n[[Unique Note]]\n@missing.md\n",
        )
        guide = self.write(
            root / "docs" / "Guide With Spaces.md",
            "Return to [the instructions](../AGENTS.md).\nAlso read `Other.md`.\n",
        )
        other = self.write(root / "docs" / "Other.md", "Nothing mandatory here.\n")
        note = self.write(root / "notes" / "Unique Note.md", "A unique wiki target.\n")

        result = self.run_discovery(root)

        self.assertEqual(result["schema_version"], "1.0")
        paths = {item["path"] for item in result["files"]}
        self.assertEqual(paths, {str(path.resolve()) for path in (agents, guide, other, note)})
        statuses = {(item["reference"], item["status"]) for item in result["links"]}
        self.assertIn(("docs/Guide With Spaces.md", "found"), statuses)
        self.assertIn(("Unique Note", "found"), statuses)
        self.assertIn(("missing.md", "missing"), statuses)
        self.assertLess(len(result["files"]), 10, "the link cycle must terminate")

    def test_candidate_signals_are_hints_without_findings_or_scores(self) -> None:
        root = self.base / "signals"
        source = self.write(
            root / "AGENTS.md",
            "Always use this workflow.\n"
            "You must read HANDBOOK.md before starting.\n"
            "Ask the user for confirmation.\n"
            "CI must pass.\n"
            "Ordinary descriptive prose.\n",
        )

        result = self.run_discovery(source)

        record = result["files"][0]
        kinds = {signal["kind"] for signal in record["candidate_signals"]}
        self.assertEqual(
            kinds,
            {"broad_trigger", "universal_read", "confirmation_gate", "required_check"},
        )
        self.assertNotIn("findings", result)
        self.assertNotIn("severity", json.dumps(result))
        self.assertEqual(record["candidate_signals"][0]["quote"], "Always use this workflow.")

    def test_candidate_signal_quote_preserves_source_indentation(self) -> None:
        source = self.write(self.base / "indented" / "AGENTS.md", "    Always use this workflow.  \n")

        result = self.run_discovery(source)

        self.assertEqual(
            result["files"][0]["candidate_signals"][0]["quote"],
            "    Always use this workflow.  ",
        )

    def test_skills_sh_exclusion_is_path_based_and_follows_symlinks(self) -> None:
        managed = self.write(
            self.home / ".agents" / "skills" / "reviewer" / "SKILL.md",
            "Managed skill body.\n",
        )
        self.write(
            self.home / ".agents" / ".skill-lock.json",
            json.dumps({"version": 1, "skills": {"reviewer": {"source": "example/repo"}}}),
        )
        root = self.base / "project"
        authored = self.write(root / "authored" / "reviewer" / "SKILL.md", "Authored fork.\n")
        root.mkdir(exist_ok=True)
        (root / "managed-alias").symlink_to(managed.parent, target_is_directory=True)

        result = self.run_discovery(root)

        self.assertIn(str(authored.resolve()), {item["path"] for item in result["files"]})
        self.assertIn(str(managed.parent.resolve()), {item["path"] for item in result["excluded"]})
        excluded = next(item for item in result["excluded"] if item["path"] == str(managed.parent.resolve()))
        self.assertEqual(excluded["reason"], "skills.sh managed skill")

    def test_authored_plugin_skill_is_excluded_but_root_instructions_remain(self) -> None:
        root = self.base / "plugin-source"
        agents = self.write(root / "AGENTS.md", "Repository contributor instructions.\n")
        skill = self.write(root / "skills" / "example" / "SKILL.md", "Plugin skill instructions.\n")
        self.write(root / ".claude-plugin" / "plugin.json", json.dumps({"name": "portable"}))

        result = self.run_discovery(root)

        self.assertIn(str(agents.resolve()), {item["path"] for item in result["files"]})
        self.assertNotIn(str(skill.resolve()), {item["path"] for item in result["files"]})
        excluded = {item["path"]: item for item in result["excluded"]}
        self.assertIn(str(skill.parents[1].resolve()), excluded)
        self.assertEqual(excluded[str(skill.parents[1].resolve())]["reason"], "plugin skill component")

    def test_plugin_manifest_cannot_classify_the_whole_repo_as_a_skill(self) -> None:
        root = self.base / "plugin-with-broad-component"
        agents = self.write(root / "AGENTS.md", "Repository instructions.\n")
        self.write(
            root / ".codex-plugin" / "plugin.json",
            json.dumps({"name": "portable", "skills": "."}),
        )

        result = self.run_discovery(root)

        self.assertIn(str(agents.resolve()), {item["path"] for item in result["files"]})
        self.assertTrue(any("must be below the plugin root" in item for item in result["warnings"]))

    def test_symlinked_entry_files_are_deduplicated_with_aliases(self) -> None:
        root = self.base / "aliases"
        original = self.write(root / "AGENTS.md", "Shared instructions.\n")
        alias = root / "CLAUDE.md"
        alias.symlink_to(original.name)

        result = self.run_discovery(root)

        self.assertEqual(len(result["files"]), 1)
        self.assertEqual(
            set(result["files"][0]["aliases"]),
            {str(original.absolute()), str(alias.absolute())},
        )

    def test_malformed_lock_is_reported_and_unknown_content_is_included(self) -> None:
        self.write(self.home / ".agents" / ".skill-lock.json", "{broken")
        root = self.base / "unknown"
        source = self.write(root / "SKILL.md", "Locally authored instructions.\n")

        result = self.run_discovery(root)

        self.assertEqual([item["path"] for item in result["files"]], [str(source.resolve())])
        self.assertTrue(any("Could not parse skills.sh lock" in warning for warning in result["warnings"]))

    def test_runtime_plugin_root_is_excluded_even_without_registry(self) -> None:
        plugin = self.write(
            self.home / ".codex" / "plugins" / "cache" / "sample" / "SKILL.md",
            "Runtime plugin.\n",
        )

        result = self.run_discovery(plugin)

        self.assertEqual(result["roots"][0]["status"], "excluded")
        self.assertEqual(result["files"], [])
        self.assertEqual(result["excluded"][0]["reason"], "managed plugin content")

    def test_project_lock_excludes_only_the_recorded_install_directory(self) -> None:
        root = self.base / "locked-project"
        managed = self.write(root / ".agents" / "skills" / "helper" / "SKILL.md", "Installed.\n")
        authored = self.write(root / "source" / "helper" / "SKILL.md", "Authored source.\n")
        self.write(
            root / "skills-lock.json",
            json.dumps(
                {
                    "skills": {
                        "helper": {
                            "source": "example/repository",
                            "sourceType": "github",
                            "skillPath": "source/helper/SKILL.md",
                            "computedHash": "example",
                        }
                    }
                }
            ),
        )

        result = self.run_discovery(root)

        files = {item["path"] for item in result["files"]}
        self.assertIn(str(authored.resolve()), files)
        self.assertNotIn(str(managed.resolve()), files)
        self.assertIn(str(managed.parent.resolve()), {item["path"] for item in result["excluded"]})

    def test_invalid_lock_skill_name_cannot_escape_install_directory(self) -> None:
        root = self.base / "malicious-lock"
        authored = self.write(root / ".agents" / "source" / "SKILL.md", "Authored.\n")
        self.write(
            root / "skills-lock.json",
            json.dumps({"skills": {"../source": {"source": "untrusted"}}}),
        )

        result = self.run_discovery(root)

        self.assertIn(str(authored.resolve()), {item["path"] for item in result["files"]})
        self.assertTrue(any("Ignored invalid skill name" in item for item in result["warnings"]))

    def test_plugin_registry_install_path_is_used_as_provenance(self) -> None:
        installed = self.base / "third-party-cache" / "plugin"
        self.write(installed / "SKILL.md", "Installed plugin content.\n")
        self.write(
            self.home / ".claude" / "plugins" / "installed_plugins.json",
            json.dumps({"plugins": [{"name": "sample", "installPath": str(installed)}]}),
        )

        result = self.run_discovery(installed)

        self.assertEqual(result["roots"][0]["status"], "excluded")
        self.assertEqual(result["excluded"][0]["reason"], "managed plugin content")
        self.assertTrue(any("installPath" in item for item in result["excluded"][0]["evidence"]))

    def test_xdg_global_lock_resolves_installs_in_agent_directories(self) -> None:
        installed = self.write(
            self.home / ".agents" / "skills" / "xdg-helper" / "SKILL.md",
            "Installed via skills.sh.\n",
        )
        self.write(
            self.state / "skills" / ".skill-lock.json",
            json.dumps({"skills": {"xdg-helper": {"source": "example/repository"}}}),
        )

        result = self.run_discovery(installed.parent)

        self.assertEqual(result["roots"][0]["status"], "excluded")
        self.assertEqual(result["excluded"][0]["reason"], "skills.sh managed skill")
        self.assertTrue(any(str(self.state) in item for item in result["excluded"][0]["evidence"]))

    def test_custom_codex_and_claude_directories_supply_installs_and_registry(self) -> None:
        codex_home = self.base / "portable-codex"
        claude_config = self.base / "portable-claude"
        installed_skill = self.write(codex_home / "skills" / "helper" / "SKILL.md", "Installed.\n")
        claude_skill = self.write(
            claude_config / "skills" / "claude-helper" / "SKILL.md", "Installed.\n"
        )
        installed_plugin = self.write(self.base / "plugin-cache" / "SKILL.md", "Plugin.\n")
        codex_plugin = self.write(self.base / "codex-plugin-cache" / "SKILL.md", "Plugin.\n")
        self.write(
            self.state / "skills" / ".skill-lock.json",
            json.dumps(
                {
                    "skills": {
                        "helper": {"source": "example/repository"},
                        "claude-helper": {"source": "example/repository"},
                    }
                }
            ),
        )
        self.write(
            claude_config / "plugins" / "installed_plugins.json",
            json.dumps({"plugins": [{"installPath": str(installed_plugin.parent)}]}),
        )
        self.write(
            codex_home / "plugins" / "installed_plugins.json",
            json.dumps({"plugins": [{"installPath": str(codex_plugin.parent)}]}),
        )
        environment = {
            "CODEX_HOME": str(codex_home),
            "CLAUDE_CONFIG_DIR": str(claude_config),
        }

        skill_result = self.run_discovery(installed_skill.parent, extra_environment=environment)
        claude_skill_result = self.run_discovery(
            claude_skill.parent, extra_environment=environment
        )
        plugin_result = self.run_discovery(installed_plugin.parent, extra_environment=environment)
        codex_plugin_result = self.run_discovery(
            codex_plugin.parent, extra_environment=environment
        )

        self.assertEqual(skill_result["excluded"][0]["reason"], "skills.sh managed skill")
        self.assertEqual(
            claude_skill_result["excluded"][0]["reason"], "skills.sh managed skill"
        )
        self.assertEqual(plugin_result["excluded"][0]["reason"], "managed plugin content")
        self.assertEqual(
            codex_plugin_result["excluded"][0]["reason"], "managed plugin content"
        )

    def test_authored_directory_symlink_is_traversed(self) -> None:
        external = self.base / "authored-source"
        skill = self.write(external / "nested" / "SKILL.md", "Authored skill.\n")
        root = self.base / "symlink-project"
        root.mkdir()
        (root / "shared-skills").symlink_to(external, target_is_directory=True)
        (external / "back-to-project").symlink_to(root, target_is_directory=True)

        result = self.run_discovery(root)

        self.assertIn(str(skill.resolve()), {item["path"] for item in result["files"]})

    def test_nested_project_lock_excludes_nested_install(self) -> None:
        root = self.base / "monorepo"
        project = root / "packages" / "example"
        managed = self.write(project / ".agents" / "skills" / "nested" / "SKILL.md", "Installed.\n")
        self.write(
            project / "skills-lock.json",
            json.dumps({"skills": {"nested": {"source": "example/repository"}}}),
        )
        authored = self.write(project / "source" / "SKILL.md", "Authored.\n")

        result = self.run_discovery(root)

        paths = {item["path"] for item in result["files"]}
        self.assertIn(str(authored.resolve()), paths)
        self.assertNotIn(str(managed.resolve()), paths)
        self.assertIn(str(managed.parent.resolve()), {item["path"] for item in result["excluded"]})

    def test_nested_instruction_reference_falls_back_to_containing_root(self) -> None:
        root = self.base / "root-relative"
        skill = self.write(
            root / "skills" / "example" / "SKILL.md",
            "Read `docs/tenets.md`.\n@docs/policy.md\n",
        )
        tenets = self.write(root / "docs" / "tenets.md", "Tenets.\n")
        policy = self.write(root / "docs" / "policy.md", "Policy.\n")

        result = self.run_discovery(root)

        links = {
            item["reference"]: item
            for item in result["links"]
            if item["from"] == str(skill.resolve())
        }
        self.assertEqual(links["docs/tenets.md"]["status"], "found")
        self.assertEqual(links["docs/tenets.md"]["to"], str(tenets.resolve()))
        self.assertEqual(links["docs/policy.md"]["to"], str(policy.resolve()))

    def test_ambiguous_root_relative_fallback_stays_unresolved(self) -> None:
        root = self.base / "outer"
        nested = root / "nested"
        skill = self.write(nested / "skills" / "example" / "SKILL.md", "Read `docs/tenets.md`.\n")
        self.write(root / "docs" / "tenets.md", "Outer.\n")
        self.write(nested / "docs" / "tenets.md", "Nested.\n")

        result = self.run_discovery(root, nested)

        links = [item for item in result["links"] if item["from"] == str(skill.resolve())]
        self.assertTrue(any(item["status"] == "unresolved" for item in links))
        self.assertTrue(any("Ambiguous root-relative reference" in item for item in result["warnings"]))

    def test_root_relative_managed_target_is_recorded_as_excluded(self) -> None:
        root = self.base / "plugin-reference"
        source = self.write(
            root / "docs" / "AGENTS.md",
            "See `skills/plugin/SKILL.md`.\n",
        )
        managed = self.write(
            root / "skills" / "plugin" / "SKILL.md",
            "Plugin instructions.\n",
        )
        self.write(root / ".codex-plugin" / "plugin.json", json.dumps({"name": "plugin"}))

        result = self.run_discovery(root)

        link = next(item for item in result["links"] if item["from"] == str(source.resolve()))
        self.assertEqual(link["status"], "excluded")
        self.assertEqual(link["to"], str(managed.resolve()))

    def test_folder_qualified_extensionless_obsidian_reference_resolves(self) -> None:
        root = self.base / "obsidian-qualified"
        source = self.write(root / "nested" / "AGENTS.md", "Read [[docs/guide]].\n")
        guide = self.write(root / "notes" / "docs" / "guide.md", "Guide.\n")

        result = self.run_discovery(root)

        link = next(item for item in result["links"] if item["from"] == str(source.resolve()))
        self.assertEqual(link["status"], "found")
        self.assertEqual(link["to"], str(guide.resolve()))

    def test_obsidian_broad_search_does_not_walk_plugin_skill_tree(self) -> None:
        root = self.base / "obsidian-plugin"
        source = self.write(root / "docs" / "AGENTS.md", "Read [[hidden-guide]].\n")
        self.write(
            root / "skills" / "plugin" / "hidden-guide.md",
            "Managed plugin guide.\n",
        )
        self.write(root / ".claude-plugin" / "plugin.json", json.dumps({"name": "plugin"}))

        result = self.run_discovery(root)

        link = next(item for item in result["links"] if item["from"] == str(source.resolve()))
        self.assertEqual(link["status"], "missing")

    def test_refuses_to_overwrite_input_or_provenance_metadata(self) -> None:
        root = self.base / "protected"
        source = self.write(root / "AGENTS.md", "Always preserve this.\n")
        lock = self.write(root / "skills-lock.json", json.dumps({"skills": {}}))
        manifest = self.write(
            root / ".claude-plugin" / "plugin.json", json.dumps({"name": "protected"})
        )
        environment = os.environ.copy()
        environment.update(
            HOME=str(self.home),
            XDG_STATE_HOME=str(self.state),
            CODEX_HOME=str(self.home / ".codex"),
            CLAUDE_CONFIG_DIR=str(self.home / ".claude"),
        )

        originals = {path: path.read_text(encoding="utf-8") for path in (source, lock, manifest)}
        for protected in originals:
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), str(root), "--output", str(protected)],
                env=environment,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn("Refusing to overwrite", completed.stderr)
        for protected, original in originals.items():
            self.assertEqual(protected.read_text(encoding="utf-8"), original)

    def test_builtin_codex_system_skill_is_excluded(self) -> None:
        builtin = self.write(
            self.home / ".codex" / "skills" / ".system" / "creator" / "SKILL.md",
            "Built in.\n",
        )

        result = self.run_discovery(builtin.parent)

        self.assertEqual(result["roots"][0]["status"], "excluded")
        self.assertEqual(result["excluded"][0]["reason"], "managed runtime skill")

    def test_link_budget_marks_skipped_target_unresolved(self) -> None:
        scripts = str(SCRIPT.parent)
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        import discover

        root = self.base / "budget"
        self.write(root / "AGENTS.md", "[one](one.md)\n[two](two.md)\n")
        self.write(root / "one.md", "One.\n")
        self.write(root / "two.md", "Two.\n")
        previous = discover.MAX_LINKED_FILES
        environment = {
            "HOME": str(self.home),
            "XDG_STATE_HOME": str(self.state),
            "CODEX_HOME": str(self.home / ".codex"),
            "CLAUDE_CONFIG_DIR": str(self.home / ".claude"),
        }
        try:
            discover.MAX_LINKED_FILES = 1
            with mock.patch.dict(os.environ, environment, clear=False):
                result = discover.Discovery([root]).run()
        finally:
            discover.MAX_LINKED_FILES = previous

        statuses = {item["reference"]: item["status"] for item in result["links"]}
        self.assertEqual(statuses["one.md"], "found")
        self.assertEqual(statuses["two.md"], "unresolved")
        self.assertTrue(any("map is incomplete" in item for item in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
