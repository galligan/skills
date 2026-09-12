"""Read-only repository-affiliation hints; never decide audit inclusion or authorship."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit


def command(args: list[str]) -> tuple[int, str]:
    environment = os.environ.copy()
    environment.update(GIT_TERMINAL_PROMPT="0", GH_PROMPT_DISABLED="1")
    # A caller's repository-routing variables must not redirect inspection elsewhere.
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
        environment.pop(name, None)
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=15, env=environment)
        return result.returncode, result.stdout
    except (OSError, subprocess.TimeoutExpired, UnicodeError):
        return -1, ""


def github_repository(raw: str) -> tuple[str, str] | None:
    """Parse common GitHub remotes without retaining credentials or query strings."""
    if "://" not in raw:
        match = re.fullmatch(r"(?:[^@/:]+@)?github\.com:(.+)", raw, re.IGNORECASE)
        if not match:
            return None
        path = match[1]
    else:
        try:
            parsed = urlsplit(raw)
            if parsed.hostname is None or parsed.hostname.lower() != "github.com":
                return None
            path = parsed.path.lstrip("/")
        except ValueError:
            return None
    match = re.fullmatch(r"([A-Za-z0-9-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?", path)
    return (match[1], match[2]) if match else None


class OwnershipIndex:
    def __init__(self) -> None:
        self.context = {"host": "github.com", "status": "not_checked", "user": None,
                        "organizations": {"status": "not_checked", "logins": []},
                        "reason": "GitHub identity is checked only when a mapped file has a GitHub remote."}
        self.directories: dict[Path, Path | None] = {}
        self.repositories: dict[Path, tuple[list[dict], bool]] = {}

    def _identity(self) -> None:
        if self.context["status"] != "not_checked":
            return
        code, user = command(["gh", "api", "--hostname", "github.com", "user", "--jq", ".login"])
        user = user.strip()
        if code or not re.fullmatch(r"[A-Za-z0-9-]+", user):
            self.context.update(status="unavailable", reason="Authenticated GitHub identity is unavailable; no login or permission change was attempted.")
            return
        code, organizations = command(["gh", "api", "--hostname", "github.com", "user/orgs?per_page=100", "--paginate", "--jq", ".[].login"])
        orgs = organizations.splitlines()
        if code or any(not re.fullmatch(r"[A-Za-z0-9-]+", org) for org in orgs):
            self.context.update(status="partial", user={"login": user},
                                organizations={"status": "unavailable", "logins": []}, reason="User identified, but organization lookup failed or was incomplete; only a direct user match is established.")
        else:
            self.context.update(status="available", user={"login": user},
                                organizations={"status": "available", "logins": sorted(set(orgs), key=str.casefold)},
                                reason="Affiliations visible to the current github.com credentials; token permissions may hide organizations. Remote affiliation does not establish file authorship.")

    def _repository(self, directory: Path) -> Path | None:
        if directory not in self.directories:
            code, root = command(["git", "-C", str(directory), "rev-parse", "--show-toplevel"])
            self.directories[directory] = Path(root.strip()).resolve() if code == 0 and root.strip() else None
        return self.directories[directory]

    def _remotes(self, root: Path) -> tuple[list[dict], bool]:
        if root not in self.repositories:
            code, output = command(["git", "-C", str(root), "config", "--get-regexp", r"^remote\..*\.url$"])
            remotes, unknown = [], code not in (0, 1)
            for line in output.splitlines() if code == 0 else []:
                match = re.fullmatch(r"remote\.(.+)\.url\s+(.+)", line)
                parsed = github_repository(match[2]) if match else None
                if parsed:
                    owner, repository = parsed
                    remotes.append({"name": match[1], "host": "github.com",
                                    "repository": f"{owner}/{repository}",
                                    "url": f"https://github.com/{owner}/{repository}",
                                    "owner": {"login": owner, "relationship": "unknown"}})
                else:
                    unknown = True
            self.repositories[root] = (remotes, unknown)
        return self.repositories[root]

    def _remote_relationship(self, remote: dict) -> dict:
        login = remote["owner"]["login"]
        relationship = "unknown"
        user = self.context["user"]
        if user and login.casefold() == user["login"].casefold():
            relationship = "authenticated_user"
        elif self.context["organizations"]["status"] == "available":
            organizations = {org.casefold() for org in self.context["organizations"]["logins"]}
            relationship = "user_organization" if login.casefold() in organizations else "not_in_known_affiliations"
        # Keep cached remote metadata independent of a file's classification.
        return dict(remote, owner={"login": login, "relationship": relationship})

    def inspect(self, path: Path) -> dict:
        path = path.resolve()
        result = {"repository_affiliation": "unknown", "possible_external_source": None,
                  "repository": None, "tracked": None, "remotes": [],
                  "reason": "No accessible Git worktree; repository affiliation is unknown."}
        root = self._repository(path.parent)
        if root is None:
            return result
        result["repository"] = str(root)
        code, _ = command(["git", "--literal-pathspecs", "-C", str(root), "ls-files", "--error-unmatch", "--", str(path)])
        result["tracked"] = True if code == 0 else False if code == 1 else None
        remotes, unknown_remotes = self._remotes(root)
        if not remotes:
            result["reason"] = "No recognized github.com remote; affiliation is unknown."
            return result
        self._identity()
        result["remotes"] = [self._remote_relationship(remote) for remote in remotes]
        if result["tracked"] is not True:
            result["reason"] = "File is untracked or tracking could not be established; enclosing repository remotes are context only."
            return result
        if self.context["user"] is None:
            result["reason"] = self.context["reason"]
            return result
        relationships = {remote["owner"]["relationship"] for remote in result["remotes"]}
        if "not_in_known_affiliations" in relationships:
            result.update(repository_affiliation="has_external_remote", possible_external_source=True,
                          reason="Tracked file has a remote outside the user's visible GitHub affiliations. Forks and additional remotes are possible; this is an advisory source signal, not proof of authorship.")
        elif "unknown" in relationships or unknown_remotes:
            result["reason"] = "Some remote affiliations could not be determined; inspect the known relationships and GitHub lookup status."
        else:
            result.update(repository_affiliation="matches_user_or_org", possible_external_source=False,
                          reason="Recognized remotes match the user or a visible organization. This does not prove the file was authored by the user or rule out copied content.")
        return result
