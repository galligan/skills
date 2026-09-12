#!/usr/bin/env python3
"""Build an evidence map of portable agent-instruction audit candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import deque
from pathlib import Path
from urllib.parse import unquote, urlparse

from ownership import OwnershipIndex
from provenance import ProvenanceIndex


ENTRY_NAMES = {
    "AGENTS.md",
    "CLAUDE.md",
    "SKILL.md",
    "GEMINI.md",
    ".cursorrules",
    ".windsurfrules",
}
ENTRY_RELATIVE_PATHS = {Path(".github/copilot-instructions.md")}
IGNORED_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "vendor",
    "build",
    "dist",
    "target",
    "DerivedData",
    "Pods",
    "__pycache__",
}
MAX_LINKED_FILES = 10_000

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+(?: [^)]*?)?))(?:\s+[\"'][^\"']*[\"'])?\)")
OBSIDIAN_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
IMPORT_RE = re.compile(r"(?<!\w)@(?:import\s+)?(?:<([^>]+)>|([^\s`]+\.md\b))", re.IGNORECASE)
BACKTICK_MD_RE = re.compile(r"`([^`\n]+\.(?:md|mdc)(?:#[^`\n]+)?)`", re.IGNORECASE)

SIGNALS = (
    (
        "broad_trigger",
        re.compile(r"\b(?:always|whenever|when (?:the user )?(?:asks|requests)|for (?:all|any|every) (?:task|request)|in all cases|must use)\b", re.IGNORECASE),
    ),
    (
        "universal_read",
        re.compile(r"\b(?:(?:always|must|required to) read|read .{0,80}(?:before (?:starting|doing|proceeding)|\bfirst\b)|start by reading)\b", re.IGNORECASE),
    ),
    (
        "confirmation_gate",
        re.compile(r"\b(?:ask (?:the user )?(?:for )?(?:permission|confirmation|approval)|confirm (?:with the user )?before|wait for (?:permission|confirmation|approval)|do not proceed without (?:permission|confirmation|approval))\b", re.IGNORECASE),
    ),
    (
        "required_check",
        re.compile(r"\b(?:(?:must|required to|always) (?:run|verify|check) .{0,100}(?:test|lint|build|check|CI)|CI must pass|checks? (?:must (?:pass|be green)|are green)|run (?:all|the full) (?:tests?|checks?))\b", re.IGNORECASE),
    ),
)


def _absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.path.expanduser(str(path))))


class Discovery:
    def __init__(self, roots: list[Path]) -> None:
        self.input_roots = [_absolute(root) for root in roots]
        self.provenance = ProvenanceIndex(self.input_roots)
        self.root_records: list[dict[str, str]] = []
        self.files: dict[Path, dict[str, object]] = {}
        self.excluded: dict[Path, dict[str, object]] = {}
        self.links: list[dict[str, str]] = []
        self.warnings = list(self.provenance.warnings)
        self.queue: deque[tuple[Path, str, Path]] = deque()
        self.processed: set[Path] = set()
        self.linked_scheduled: set[Path] = set()
        self.linked_count = 0
        self.search_roots = [root if root.is_dir() else root.parent for root in self.input_roots]

    def run(self) -> dict[str, object]:
        for root in self.input_roots:
            self._add_root(root)
        while self.queue:
            lexical, kind, via = self.queue.popleft()
            self._process_file(lexical, kind, via)
        ownership = OwnershipIndex()
        for record in self.files.values():
            record["ownership"] = ownership.inspect(Path(str(record["path"])))
        return {
            "schema_version": "1.0",
            "ownership_context": ownership.context,
            "roots": self.root_records,
            "files": sorted(self.files.values(), key=lambda item: str(item["path"])),
            "excluded": sorted(self.excluded.values(), key=lambda item: str(item["path"])),
            "links": self.links,
            "warnings": self.warnings,
        }

    def _add_root(self, root: Path) -> None:
        if not root.exists() and not root.is_symlink():
            self.root_records.append({"path": str(root), "status": "missing"})
            self.warnings.append(f"Explicit root does not exist: {root}")
            return
        exclusion = self.provenance.exclusion(root)
        if exclusion:
            self.root_records.append({"path": str(root), "status": "excluded"})
            self._exclude(root, *exclusion)
            return
        self.root_records.append({"path": str(root), "status": "found"})
        if root.is_file():
            self.queue.append((root, "entry", root))
            return
        self._walk_root(root)

    def _walk_root(self, root: Path) -> None:
        visited: set[Path] = set()

        def on_error(error: OSError) -> None:
            self.warnings.append(
                f"Could not inspect directory while discovering instructions: {error}"
            )

        for directory, names, filenames in os.walk(
            root, followlinks=True, onerror=on_error
        ):
            current = Path(directory)
            canonical = current.resolve(strict=False)
            if canonical in visited:
                names[:] = []
                continue
            visited.add(canonical)
            kept: list[str] = []
            for name in names:
                candidate = current / name
                exclusion = self.provenance.exclusion(candidate)
                if name in IGNORED_DIRECTORIES:
                    self._exclude(candidate, "dependency, build, or VCS artifact", [f"ignored directory name: {name}"])
                elif exclusion:
                    self._exclude(candidate, *exclusion)
                else:
                    kept.append(name)
            names[:] = kept
            for name in filenames:
                candidate = current / name
                relative = candidate.relative_to(root)
                in_cursor_rules = (
                    len(relative.parts) >= 3
                    and relative.parts[:2] == (".cursor", "rules")
                    and candidate.suffix == ".mdc"
                )
                in_github_rules = (
                    len(relative.parts) >= 3
                    and relative.parts[:2] == (".github", "instructions")
                    and name.endswith(".instructions.md")
                )
                if (
                    name in ENTRY_NAMES
                    or relative in ENTRY_RELATIVE_PATHS
                    or in_cursor_rules
                    or in_github_rules
                ):
                    self.queue.append((candidate, "entry", root))

    def _process_file(self, lexical: Path, kind: str, via: Path) -> None:
        exclusion = self.provenance.exclusion(lexical)
        if exclusion:
            self._exclude(lexical, *exclusion)
            return
        try:
            canonical = lexical.resolve(strict=True)
        except (OSError, RuntimeError) as error:
            self.warnings.append(f"Could not resolve instruction file {lexical}: {error}")
            return
        if not canonical.is_file():
            self.warnings.append(f"Instruction target is not a file: {lexical}")
            return
        exclusion = self.provenance.exclusion(canonical)
        if exclusion:
            self._exclude(lexical, *exclusion)
            return
        alias = str(_absolute(lexical))
        if canonical in self.files:
            record = self.files[canonical]
            aliases = record["aliases"]
            vias = record["via"]
            assert isinstance(aliases, list) and isinstance(vias, list)
            if alias not in aliases:
                aliases.append(alias)
                aliases.sort()
            via_text = str(_absolute(via))
            if via_text not in vias:
                vias.append(via_text)
                vias.sort()
            if kind == "entry":
                record["kind"] = "entry"
            return
        try:
            raw = canonical.read_bytes()
            text = raw.decode("utf-8")
        except (OSError, UnicodeError) as error:
            self.warnings.append(f"Could not read instruction file {canonical}: {error}")
            return
        lines = text.splitlines()
        record: dict[str, object] = {
            "path": str(canonical),
            "aliases": [alias],
            "kind": kind,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "lines": len(lines),
            "via": [str(_absolute(via))],
            "candidate_signals": self._signals(lines),
        }
        self.files[canonical] = record
        if canonical in self.processed:
            return
        self.processed.add(canonical)
        self._follow_links(canonical, text)

    @staticmethod
    def _signals(lines: list[str]) -> list[dict[str, object]]:
        found: list[dict[str, object]] = []
        for number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            for kind, pattern in SIGNALS:
                if pattern.search(line):
                    found.append(
                        {"line_start": number, "line_end": number, "kind": kind, "quote": line}
                    )
        return found

    def _follow_links(self, source: Path, text: str) -> None:
        references: list[tuple[str, str]] = []
        for match in MARKDOWN_LINK_RE.finditer(text):
            references.append((match.group(1) or match.group(2), "markdown"))
        references.extend((match.group(1), "obsidian") for match in OBSIDIAN_RE.finditer(text))
        for match in IMPORT_RE.finditer(text):
            references.append((match.group(1) or match.group(2), "import"))
        references.extend((match.group(1), "backtick") for match in BACKTICK_MD_RE.finditer(text))

        seen: set[tuple[str, str]] = set()
        for raw, reference_kind in references:
            raw = raw.strip()
            key = (raw, reference_kind)
            if not raw or key in seen:
                continue
            seen.add(key)
            self._follow_reference(source, raw, reference_kind)

    def _follow_reference(self, source: Path, raw: str, reference_kind: str) -> None:
        parsed = urlparse(raw)
        link: dict[str, str] = {"from": str(source), "reference": raw, "status": "unresolved"}
        if parsed.scheme or raw.startswith("//"):
            link["status"] = "external"
            self.links.append(link)
            return
        path_text = unquote(raw.split("#", 1)[0]).strip()
        if not path_text:
            return
        reference_path = Path(path_text)
        candidate = (
            _absolute(reference_path)
            if reference_path.is_absolute()
            else source.parent / reference_path
        )
        candidate = _absolute(candidate)
        if reference_kind == "obsidian" and not candidate.exists() and not reference_path.suffix:
            direct_markdown = candidate.with_suffix(".md")
            if direct_markdown.exists() or direct_markdown.is_symlink():
                candidate = direct_markdown
        if (
            not candidate.exists()
            and not reference_path.is_absolute()
            and reference_path.parts
            and reference_path.parts[0] not in {".", ".."}
        ):
            fallbacks = self._root_relative_matches(
                source,
                reference_path,
                markdown_suffix=reference_kind == "obsidian",
            )
            if len(fallbacks) == 1:
                candidate = fallbacks[0]
            elif len(fallbacks) > 1:
                link["status"] = "unresolved"
                self.links.append(link)
                options = ", ".join(str(path) for path in fallbacks)
                self.warnings.append(
                    f"Ambiguous root-relative reference {raw!r} from {source}: {options}"
                )
                return
        if reference_kind == "obsidian" and not candidate.exists():
            matches = self._unique_obsidian_matches(path_text)
            if len(matches) == 1:
                candidate = matches[0]
            elif len(matches) > 1:
                self.warnings.append(f"Ambiguous Obsidian reference {raw!r} from {source}.")
                self.links.append(link)
                return
        if not candidate.exists() and not candidate.is_symlink():
            link.update(status="missing", to=str(candidate))
            self.links.append(link)
            return
        exclusion = self.provenance.exclusion(candidate)
        if exclusion:
            link.update(status="excluded", to=str(candidate.resolve(strict=False)))
            self.links.append(link)
            self._exclude(candidate, *exclusion)
            return
        if not candidate.is_file():
            self.links.append(link)
            return
        canonical = candidate.resolve(strict=False)
        if canonical not in self.files and canonical not in self.linked_scheduled:
            if self.linked_count >= MAX_LINKED_FILES:
                link.update(status="unresolved", to=str(canonical))
                self.links.append(link)
                message = (
                    f"Linked-file traversal stopped after {MAX_LINKED_FILES} files; "
                    "the map is incomplete. Narrow the roots or split the audit."
                )
                if message not in self.warnings:
                    self.warnings.append(message)
                return
            self.linked_count += 1
            self.linked_scheduled.add(canonical)
        link.update(status="found", to=str(canonical))
        self.links.append(link)
        self.queue.append((candidate, "linked", source))

    def _root_relative_matches(
        self, source: Path, reference: Path, *, markdown_suffix: bool = False
    ) -> list[Path]:
        matches: set[Path] = set()
        source_canonical = source.resolve(strict=False)
        for root in self.search_roots:
            root_canonical = root.resolve(strict=False)
            try:
                source_canonical.relative_to(root_canonical)
            except ValueError:
                continue
            candidates = [root_canonical / reference]
            if markdown_suffix and not reference.suffix:
                candidates.append((root_canonical / reference).with_suffix(".md"))
            for candidate in candidates:
                if candidate.is_file():
                    matches.add(candidate.resolve(strict=False))
        return sorted(matches)

    def _unique_obsidian_matches(self, raw: str) -> list[Path]:
        requested = Path(raw)
        names = {requested.name}
        if not requested.suffix:
            names.add(f"{requested.name}.md")
        matches: set[Path] = set()
        for root in self.search_roots:
            if not root.is_dir():
                continue
            visited: set[Path] = set()

            def on_error(error: OSError) -> None:
                self.warnings.append(
                    f"Could not inspect directory while resolving Obsidian reference: {error}"
                )

            for directory, dirnames, filenames in os.walk(
                root, followlinks=True, onerror=on_error
            ):
                current = Path(directory)
                canonical = current.resolve(strict=False)
                if canonical in visited:
                    dirnames[:] = []
                    continue
                visited.add(canonical)
                dirnames[:] = [
                    name
                    for name in dirnames
                    if name not in IGNORED_DIRECTORIES
                    and not self.provenance.exclusion(current / name)
                ]
                for name in names.intersection(filenames):
                    candidate = Path(directory) / name
                    if requested.parent != Path("."):
                        endings = {str(requested)}
                        if not requested.suffix:
                            endings.add(str(requested.with_suffix(".md")))
                        if not any(str(candidate).endswith(ending) for ending in endings):
                            continue
                    if not self.provenance.exclusion(candidate):
                        matches.add(candidate.resolve(strict=False))
        return sorted(matches)

    def _exclude(self, path: Path, reason: str, evidence: list[str]) -> None:
        canonical = path.resolve(strict=False)
        record = self.excluded.get(canonical)
        if record is None:
            self.excluded[canonical] = {
                "path": str(canonical),
                "reason": reason,
                "evidence": list(dict.fromkeys(evidence)),
            }
            return
        existing = record["evidence"]
        assert isinstance(existing, list)
        for item in evidence:
            if item not in existing:
                existing.append(item)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Discover auditable agent instructions and candidate review signals."
    )
    parser.add_argument("roots", metavar="ROOT", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path, help="JSON map to write")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    discovery = Discovery(args.roots)
    result = discovery.run()
    output = _absolute(args.output).resolve(strict=False)
    protected = set(discovery.provenance.metadata_paths)
    protected.update(
        root.resolve(strict=False)
        for root in discovery.input_roots
        if root.is_file() or root.is_symlink()
    )
    protected.update(Path(item["path"]) for item in result["files"])
    if output in protected:
        print(
            f"Refusing to overwrite discovery source or provenance metadata: {output}",
            file=sys.stderr,
        )
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
