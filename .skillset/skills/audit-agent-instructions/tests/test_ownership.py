"""Exercise affiliation signals with real local Git repositories and stubbed GitHub."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ownership


class OwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "SKILL.md"
        self.source.write_text("An instruction.\n")
        self.git("init", "--quiet")
        self.git("add", "SKILL.md")
        self.api_calls = []
        self.user_reply = (0, "example-user\n")
        self.org_reply = (0, "example-org\nsecond-org\n")
        real_command = ownership.command

        def stub(args):
            if args[0] == "gh":
                self.api_calls.append(args)
                return self.org_reply if any(x.startswith("user/orgs") for x in args) else self.user_reply
            return real_command(args)

        self.stub = patch.object(ownership, "command", side_effect=stub)
        self.stub.start()
        self.addCleanup(self.stub.stop)

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True)

    def remote(self, owner, name="origin"):
        self.git("remote", "add", name, f"git@github.com:{owner}/instructions.git")

    def test_user_and_visible_org_are_affiliated_case_insensitively(self):
        self.remote("EXAMPLE-USER")
        self.remote("SECOND-ORG", "org")
        index = ownership.OwnershipIndex()
        result = index.inspect(self.source)
        self.assertEqual(result["repository_affiliation"], "matches_user_or_org")
        self.assertFalse(result["possible_external_source"])
        self.assertEqual(index.context["user"], {"login": "example-user"})
        self.assertEqual(index.context["organizations"], {
            "status": "available", "logins": ["example-org", "second-org"]})
        self.assertEqual([r["owner"]["relationship"] for r in result["remotes"]],
                         ["authenticated_user", "user_organization"])
        self.assertEqual(result["remotes"][1]["owner"]["login"], "SECOND-ORG")
        self.assertEqual(result["remotes"][0]["url"], "https://github.com/EXAMPLE-USER/instructions")
        self.assertIn("--paginate", self.api_calls[1])

    def test_external_source_is_flagged_but_file_unchanged(self):
        self.remote("external-author")
        original = self.source.read_bytes()
        result = ownership.OwnershipIndex().inspect(self.source)
        self.assertTrue(result["possible_external_source"])
        self.assertEqual(result["remotes"][0]["owner"], {"login": "external-author", "relationship": "not_in_known_affiliations"})
        self.assertEqual(result["repository_affiliation"], "has_external_remote")
        self.assertEqual(self.source.read_bytes(), original)

    def test_own_fork_with_external_upstream_keeps_both_signals(self):
        self.remote("example-user")
        self.remote("upstream-author", "upstream")
        result = ownership.OwnershipIndex().inspect(self.source)
        self.assertTrue(result["possible_external_source"])
        self.assertEqual(len(result["remotes"]), 2)
        self.assertEqual([r["owner"]["relationship"] for r in result["remotes"]], ["authenticated_user", "not_in_known_affiliations"])

    def test_api_failure_is_unknown_and_does_not_prompt(self):
        self.remote("external-author")
        self.user_reply = (1, "")
        index = ownership.OwnershipIndex()
        self.assertIsNone(index.inspect(self.source)["possible_external_source"])
        self.assertEqual(index.context["status"], "unavailable")
        self.assertEqual(len(self.api_calls), 1)
        self.assertTrue(all(c[1] == "api" for c in self.api_calls))

    def test_partial_org_lookup_does_not_make_false_external_claim(self):
        self.remote("hidden-org")
        self.org_reply = (1, "partial-results\n")
        index = ownership.OwnershipIndex()
        self.assertEqual(index.inspect(self.source)["repository_affiliation"], "unknown")
        self.assertEqual(index.context["organizations"], {"status": "unavailable", "logins": []})
        self.assertEqual(index.context["status"], "partial")

    def test_partial_org_lookup_still_allows_direct_user_match(self):
        self.remote("example-user")
        self.org_reply = (1, "")
        self.assertEqual(ownership.OwnershipIndex().inspect(self.source)["repository_affiliation"], "matches_user_or_org")

    def test_partial_lookup_keeps_known_and_unknown_remote_relationships(self):
        self.remote("example-user")
        self.remote("hidden-org", "upstream")
        self.org_reply = (1, "")
        result = ownership.OwnershipIndex().inspect(self.source)
        self.assertEqual(result["repository_affiliation"], "unknown")
        self.assertIsNone(result["possible_external_source"])
        self.assertEqual([r["owner"]["relationship"] for r in result["remotes"]],
                         ["authenticated_user", "unknown"])

    def test_untracked_file_does_not_inherit_external_ownership(self):
        self.remote("external-author")
        source = self.root / "NEW.md"
        source.write_text("Local work")
        result = ownership.OwnershipIndex().inspect(source)
        self.assertFalse(result["tracked"])
        self.assertIsNone(result["possible_external_source"])
        self.assertEqual(result["remotes"][0]["owner"]["login"], "external-author")

    def test_no_github_remote_does_not_call_github(self):
        self.git("remote", "add", "origin", "git@gitlab.com:example/repo.git")
        self.assertEqual(ownership.OwnershipIndex().inspect(self.source)["repository_affiliation"], "unknown")
        self.assertEqual(self.api_calls, [])

    def test_untracked_glob_like_filename_is_not_mistaken_for_tracked_file(self):
        self.remote("external-author")
        source = self.root / "[S]KILL.md"
        source.write_text("Local instructions")
        result = ownership.OwnershipIndex().inspect(source)
        self.assertFalse(result["tracked"])
        self.assertIsNone(result["possible_external_source"])

    def test_identity_is_queried_once_for_multiple_files(self):
        self.remote("example-user")
        second = self.root / "AGENTS.md"
        second.write_text("More instructions")
        self.git("add", "AGENTS.md")
        index = ownership.OwnershipIndex()
        index.inspect(self.source)
        index.inspect(second)
        self.assertEqual(len(self.api_calls), 2)
        self.assertEqual(len(index.repositories), 1)

    def test_canonical_symlink_uses_target_repository(self):
        self.remote("external-author")
        alias = self.root / "linked.md"
        alias.symlink_to(self.source)
        result = ownership.OwnershipIndex().inspect(alias)
        self.assertTrue(result["tracked"])
        self.assertTrue(result["possible_external_source"])

    def test_missing_git_is_unknown_without_github_lookup(self):
        with patch.object(ownership, "command", return_value=(-1, "")):
            self.assertEqual(ownership.OwnershipIndex().inspect(self.source)["repository_affiliation"], "unknown")
        self.assertEqual(self.api_calls, [])

    def test_remote_parsing_never_retains_credentials_or_query(self):
        for url in ["git@github.com:owner/repo.git", "https://github.com/owner/repo.git", "ssh://git@github.com/owner/repo.git", "https://user:secret@github.com/owner/repo.git?access_token=secret"]:
            self.assertEqual(ownership.github_repository(url), ("owner", "repo"))
        for url in ["https://github.com.attacker.test/owner/repo", "https://gitlab.com/owner/repo", "/local/repo", "github.com:owner/repo/extra"]:
            self.assertIsNone(ownership.github_repository(url))


if __name__ == "__main__":
    unittest.main()
