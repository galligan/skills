"""Behavioral checks for evidence integrity, complete aggregation, and delivery."""

import copy
import difflib
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from consolidate import consolidate
from diffcheck import check_diff
from render import render
from validate import load_sources, validate_review


class ReportsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "AGENTS.md"
        self.source.write_text("# Project\nAlways read every manual before any task.\nKeep source files unchanged.\n")
        self.path = str(self.source)
        self.original = self.source.read_text()
        self.manifest = {"schema_version": "1.0", "roots": [{"path": str(self.root), "status": "found"}],
                         "files": [{"path": self.path, "sha256": hashlib.sha256(self.source.read_bytes()).hexdigest(), "lines": 3}],
                         "excluded": [{"path": str(self.root / ".claude/plugins"), "reason": "managed plugin content", "evidence": ["runtime location"]}],
                         "links": [], "warnings": []}
        replacement = self.original.replace("Always read every manual before any task.", "Read the manual relevant to the task.")
        self.finding = {"id": "R-001", "project": "Example", "title": "Every task loads every manual",
                        "category": "unconditional_read", "severity": "medium", "severity_reason": "Unrelated context is required for common edits.",
                        "improvement": {"level": "high", "areas": ["context", "completion"], "reason": "Scopes a pervasive prerequisite."},
                        "reach": "pervasive", "confidence": "high", "confidence_reason": "The rule has no task condition.",
                        "evidence": {"file": self.path, "line_start": 2, "line_end": 2, "quote": self.original.splitlines()[1]},
                        "related_evidence": [], "impact": "Small tasks can load unrelated manuals.",
                        "smallest_change": "Scope the read to the relevant manual.",
                        "diff": "".join(difflib.unified_diff(self.original.splitlines(True), replacement.splitlines(True), fromfile=self.path, tofile=self.path)).rstrip("\n"),
                        "decision_required": False, "decision_reason": "", "related_findings": []}
        self.review = {"schema_version": "1.0", "reviewer": "example", "findings": [self.finding],
                       "coverage": [{"path": self.path, "status": "reviewed", "reason": "Read the full instruction file."}], "unresolved": []}

    def test_more_than_ten_findings_survive_both_outputs(self):
        self.review["findings"] = [dict(copy.deepcopy(self.finding), id=f"R-{i:03}") for i in range(25)]
        result = consolidate([self.review], self.manifest, {})
        markdown = render(result)
        self.assertEqual(len(result["findings"]), 25)
        for finding in self.review["findings"]:
            self.assertIn(f"**{finding['id']} —", markdown)
        self.assertEqual(self.source.read_text(), self.original)

    def test_stale_source_and_wrong_quote_fail(self):
        self.source.write_text(self.original + "Changed later.\n")
        with self.assertRaisesRegex(ValueError, "changed since mapping"):
            consolidate([self.review], self.manifest, {})
        self.source.write_text(self.original)
        self.finding["evidence"]["quote"] = "An invented requirement."
        with self.assertRaisesRegex(ValueError, "Quote differs"):
            consolidate([self.review], self.manifest, {})

    def test_invalid_range_and_unmapped_diff_fail(self):
        self.finding["evidence"]["line_end"] = 99
        self.finding["diff"] = self.finding["diff"].replace(self.path, "/unmapped/AGENTS.md")
        errors = validate_review(self.review, {self.path: self.original})
        self.assertTrue(any("Invalid inclusive range" in e for e in errors))
        self.assertTrue(any("unmapped or ambiguous" in e for e in errors))

    def test_uncovered_file_fails(self):
        self.review["coverage"] = []
        with self.assertRaisesRegex(ValueError, "lack coverage"):
            consolidate([self.review], self.manifest, {})

    def test_decision_gates_are_validated_and_separated(self):
        self.finding["category"] = "premature_confirmation"
        with self.assertRaisesRegex(ValueError, "must be decision-required"):
            consolidate([self.review], self.manifest, {})
        self.finding.update(decision_required=True, decision_reason="Narrows an explicit approval gate.")
        output = render(consolidate([self.review], self.manifest, {}))
        self.assertLess(output.index("# Decisions:"), output.index("**R-001 —"))
        self.assertIn("1 accepted finding: 0 routine proposals and 1 decision.", output)

    def test_intentionally_excluded_root_is_not_unresolved(self):
        self.manifest["roots"].append({"path": str(self.root / ".claude/plugins"), "status": "excluded"})
        result = consolidate([self.review], self.manifest, {})
        self.assertEqual(result["unresolved"], [])
        self.assertEqual(len(result["scope"]["excluded"]), 1)

    def test_adjudication_retains_excluded_candidates(self):
        self.finding["diff"] = "A rejected malformed proposal"
        result = consolidate([self.review], self.manifest, {"R-001": {"action": "exclude", "reason": "Context makes this rule applicable."}})
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["excluded_findings"][0]["finding"], self.finding)

    def test_duplicate_ids_and_conflicting_coverage_fail(self):
        other = dict(copy.deepcopy(self.review), reviewer="other")
        with self.assertRaisesRegex(ValueError, "Duplicate finding ID"):
            consolidate([self.review, other], self.manifest, {})
        other["findings"] = []
        other["coverage"][0]["status"] = "context_only"
        with self.assertRaisesRegex(ValueError, "conflicting coverage"):
            consolidate([self.review, other], self.manifest, {})

    def test_nested_fences_remain_literal_markdown(self):
        self.finding["evidence"]["quote"] = "Before\n```bash\nrun check\n```\nAfter"
        # Rendering checks literal preservation; evidence validity is tested separately.
        result = consolidate([dict(self.review, findings=[])], self.manifest, {})
        result["findings"] = [self.finding]
        output = render(result)
        self.assertIn("````text\n" + self.finding["evidence"]["quote"] + "\n````", output)

    def test_diff_counts_positions_and_context_are_checked(self):
        check_diff(self.finding["diff"], {self.path: self.original}, self.path)
        for patch in [self.finding["diff"].replace("@@ -1,3 +1,3 @@", "@@ -1,3 +2,3 @@"),
                      self.finding["diff"].replace("-Always", "-Never")]:
            with self.assertRaises(ValueError):
                check_diff(patch, {self.path: self.original}, self.path)

    def test_additions_that_look_like_headers_and_new_files(self):
        content = "--- heading\n+++ text\n"
        patch = "".join(difflib.unified_diff(self.original.splitlines(True), (self.original + content).splitlines(True), fromfile=self.path, tofile=self.path))
        check_diff(patch, {self.path: self.original}, self.path)
        patch = f"--- /dev/null\n+++ {self.root / 'NEW.md'}\n@@ -0,0 +1,2 @@\n+one\n+two\n"
        check_diff(patch, {self.path: self.original}, self.path)
        self.assertFalse((self.root / "NEW.md").exists())

    def test_false_source_eof_marker_is_rejected(self):
        patch = self.finding["diff"].replace("-Always read every manual before any task.\n", "-Always read every manual before any task.\n\\ No newline at end of file\n")
        with self.assertRaisesRegex(ValueError, "Newline marker"):
            check_diff(patch, {self.path: self.original}, self.path)

    def test_multiple_hunks_preserve_original_coordinates(self):
        original = "\n".join(f"line {i}" for i in range(15)) + "\n"
        updated = original.replace("line 2\n", "added\nline 2\n").replace("line 12\n", "replacement\n")
        patch = "".join(difflib.unified_diff(original.splitlines(True), updated.splitlines(True), fromfile=self.path, tofile=self.path, n=1))
        check_diff(patch, {self.path: original}, self.path)

    def test_cli_produces_json_and_identical_stdout_or_file_report(self):
        for name, value in [("map.json", self.manifest), ("review.json", self.review)]:
            (self.root / name).write_text(json.dumps(value))
        destination = self.root / "findings.json"
        result = subprocess.run([sys.executable, str(SCRIPTS / "consolidate.py"), str(self.root / "review.json"),
                                 "--map", str(self.root / "map.json"), "--output", str(destination)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = self.root / "report.md"
        subprocess.run([sys.executable, str(SCRIPTS / "render.py"), str(destination), "--output", str(report)], check=True, capture_output=True)
        stdout = subprocess.run([sys.executable, str(SCRIPTS / "render.py"), str(destination)], check=True, capture_output=True, text=True)
        self.assertEqual(report.read_text(), stdout.stdout)
        self.assertEqual(json.loads(result.stdout)["path"], str(destination))

    def test_output_cannot_overwrite_audited_source(self):
        for name, value in [("map.json", self.manifest), ("review.json", self.review)]:
            (self.root / name).write_text(json.dumps(value))
        result = subprocess.run([sys.executable, str(SCRIPTS / "consolidate.py"), str(self.root / "review.json"),
                                 "--map", str(self.root / "map.json"), "--output", self.path], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.source.read_text(), self.original)

    def test_ownership_flags_are_preserved_and_rendered_without_filtering(self):
        self.manifest["ownership_context"] = {
            "host": "github.com",
            "status": "available",
            "user": {"login": "reviewer"},
            "organizations": {"status": "available", "logins": ["affiliated-org"]},
            "reason": "Authenticated GitHub affiliation was available.",
        }
        self.manifest["files"][0]["ownership"] = {
            "repository_affiliation": "has_external_remote",
            "possible_external_source": True,
            "repository": str(self.root),
            "tracked": True,
            "remotes": [
                {
                    "name": "origin",
                    "host": "github.com",
                    "repository": "reviewer/instructions",
                    "url": "https://github.com/reviewer/instructions",
                    "owner": {
                        "login": "reviewer",
                        "relationship": "authenticated_user",
                    },
                },
                {
                    "name": "company",
                    "host": "github.com",
                    "repository": "affiliated-org/instructions",
                    "url": "https://github.com/affiliated-org/instructions",
                    "owner": {
                        "login": "affiliated-org",
                        "relationship": "user_organization",
                    },
                },
                {
                    "name": "upstream",
                    "host": "github.com",
                    "repository": "outside-org/instructions",
                    "url": "https://github.com/outside-org/instructions",
                    "owner": {
                        "login": "outside-org",
                        "relationship": "not_in_known_affiliations",
                    },
                }
            ],
            "reason": "No visible affiliation matches this GitHub remote owner.",
        }

        result = consolidate([self.review], self.manifest, {})
        output = render(result)

        self.assertEqual(len(result["findings"]), 1)
        self.assertEqual(
            result["scope"]["files"][0]["ownership"]["repository_affiliation"],
            "has_external_remote",
        )
        self.assertIn("## Ownership signals", output)
        self.assertIn("User: reviewer", output)
        self.assertIn("Organizations (available): affiliated-org", output)
        self.assertIn("has\\_external\\_remote", output)
        self.assertIn("origin: reviewer/instructions", output)
        self.assertIn("owner reviewer (authenticated\\_user)", output)
        self.assertIn("company: affiliated-org/instructions", output)
        self.assertIn("owner affiliated-org (user\\_organization)", output)
        self.assertIn("upstream: outside-org/instructions", output)
        self.assertIn("owner outside-org (not\\_in\\_known\\_affiliations)", output)
        self.assertIn("possible external source yes", output)

        result["scope"]["files"][0]["ownership"] = {
            "repository_affiliation": "unknown",
            "possible_external_source": None,
            "repository": str(self.root),
            "tracked": None,
            "remotes": [],
            "reason": "Repository ownership could not be determined.",
        }
        unknown_output = render(result)
        self.assertIn("**unknown**", unknown_output)
        self.assertIn("Repository ownership could not be determined.", unknown_output)


if __name__ == "__main__":
    unittest.main()
