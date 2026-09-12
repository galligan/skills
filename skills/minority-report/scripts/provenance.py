"""Identify instruction files that belong to managed skills or plugins.

The discovery tool treats provenance metadata as evidence.  It does not infer that
an authored skill is managed merely because it has the same name as an installed
skill.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, Iterator


PLUGIN_PATH_MARKERS = (
    (".codex", "plugins"),
    (".claude", "plugins"),
    (".claude", "remote", "plugins"),
    (".chatgpt", "plugins"),
)


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _strings(value: object) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)


class ProvenanceIndex:
    """Index concrete managed-component paths without reading their bodies."""

    def __init__(self, scan_roots: Iterable[Path]) -> None:
        self.scan_roots = tuple(scan_roots)
        self.managed_roots: dict[Path, list[str]] = {}
        self.managed_plugin_roots: dict[Path, list[str]] = {}
        self.plugin_source_roots: dict[Path, list[str]] = {}
        self.runtime_skill_roots: dict[Path, list[str]] = {}
        self.runtime_plugin_roots: dict[Path, list[str]] = {}
        self.metadata_paths: set[Path] = set()
        self.warnings: list[str] = []
        self._load_global_metadata()
        self._load_plugin_source_manifests()
        self._load_project_locks()

    def exclusion(self, path: Path) -> tuple[str, list[str]] | None:
        lexical = path.absolute()
        canonical = path.resolve(strict=False)
        marker = self._runtime_plugin_marker(lexical) or self._runtime_plugin_marker(
            canonical
        )
        if marker:
            return "managed plugin content", [marker]

        for root, evidence in self.runtime_skill_roots.items():
            if _is_within(canonical, root):
                return "managed runtime skill", evidence
        for root, evidence in self.runtime_plugin_roots.items():
            if _is_within(canonical, root):
                return "managed plugin content", evidence
        for root, evidence in self.managed_plugin_roots.items():
            if _is_within(canonical, root):
                return "managed plugin content", evidence
        for root, evidence in self.managed_roots.items():
            if _is_within(canonical, root):
                return "skills.sh managed skill", evidence
        for root, evidence in self.plugin_source_roots.items():
            if _is_within(canonical, root):
                return "plugin skill component", evidence
        return None

    @staticmethod
    def _runtime_plugin_marker(path: Path) -> str | None:
        parts = path.parts
        for marker in PLUGIN_PATH_MARKERS:
            width = len(marker)
            for index in range(len(parts) - width + 1):
                if tuple(parts[index : index + width]) == marker:
                    return f"runtime plugin path marker: {'/'.join(marker)}"
        return None

    def _load_global_metadata(self) -> None:
        home = Path(os.environ.get("HOME", str(Path.home()))).expanduser()
        codex_home = Path(
            os.environ.get("CODEX_HOME", str(home / ".codex"))
        ).expanduser()
        claude_config = Path(
            os.environ.get("CLAUDE_CONFIG_DIR", str(home / ".claude"))
        ).expanduser()
        xdg_state = Path(
            os.environ.get("XDG_STATE_HOME", str(home / ".local" / "state"))
        ).expanduser()
        install_bases = tuple(
            dict.fromkeys((home / ".agents", codex_home, claude_config))
        )
        builtin = (codex_home / "skills" / ".system").resolve(strict=False)
        self.runtime_skill_roots[builtin] = [
            f"built-in Codex skill directory under CODEX_HOME: {builtin}"
        ]
        for plugin_root, label in (
            (codex_home / "plugins", "CODEX_HOME plugin directory"),
            (claude_config / "plugins", "CLAUDE_CONFIG_DIR plugin directory"),
            (claude_config / "remote" / "plugins", "CLAUDE_CONFIG_DIR remote plugin directory"),
        ):
            resolved = plugin_root.resolve(strict=False)
            self.runtime_plugin_roots.setdefault(resolved, []).append(
                f"{label}: {resolved}"
            )

        locks = [
            home / ".agents" / ".skill-lock.json",
            xdg_state / "skills" / ".skill-lock.json",
        ]
        present = False
        for lock in locks:
            if not lock.is_file():
                continue
            present = True
            self._load_skill_lock(
                lock, global_lock=True, global_install_bases=install_bases
            )
        if not present:
            locations = ", ".join(str(path) for path in locks)
            self.warnings.append(
                f"No skills.sh global lock found at {locations}; managed-skill provenance may be incomplete."
            )

        registries = tuple(
            dict.fromkeys(
                (
                    claude_config / "plugins" / "installed_plugins.json",
                    codex_home / "plugins" / "installed_plugins.json",
                )
            )
        )
        for registry in registries:
            if not registry.is_file():
                continue
            self.metadata_paths.add(registry.resolve(strict=False))
            try:
                data = json.loads(registry.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as error:
                self.warnings.append(f"Could not parse plugin registry {registry}: {error}")
                continue
            for raw in self._install_paths(data):
                candidate = Path(raw).expanduser()
                if not candidate.is_absolute():
                    candidate = registry.parent / candidate
                resolved = candidate.resolve(strict=False)
                self.managed_plugin_roots.setdefault(resolved, []).append(
                    f"installPath in {registry}"
                )

    @staticmethod
    def _install_paths(value: object) -> Iterator[str]:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "installPath" and isinstance(item, str):
                    yield item
                else:
                    yield from ProvenanceIndex._install_paths(item)
        elif isinstance(value, list):
            for item in value:
                yield from ProvenanceIndex._install_paths(item)

    def _load_project_locks(self) -> None:
        seen: set[Path] = set()
        for root in self.scan_roots:
            base = root if root.is_dir() else root.parent
            candidates = [base / "skills-lock.json"]
            # Explicit roots may point at a subdirectory in a project.
            candidates.extend(parent / "skills-lock.json" for parent in base.parents)
            for lock in candidates:
                canonical = lock.resolve(strict=False)
                if canonical in seen or not lock.is_file():
                    continue
                seen.add(canonical)
                self._load_skill_lock(lock, global_lock=False)
            if base.is_dir():
                for lock in self._walk_named_file(base, "skills-lock.json"):
                    canonical = lock.resolve(strict=False)
                    if canonical in seen:
                        continue
                    seen.add(canonical)
                    self._load_skill_lock(lock, global_lock=False)

    def _load_skill_lock(
        self,
        lock: Path,
        *,
        global_lock: bool,
        global_install_bases: tuple[Path, ...] = (),
    ) -> None:
        self.metadata_paths.add(lock.resolve(strict=False))
        try:
            data = json.loads(lock.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            self.warnings.append(f"Could not parse skills.sh lock {lock}: {error}")
            return
        skills = data.get("skills") if isinstance(data, dict) else None
        if not isinstance(skills, dict):
            self.warnings.append(f"Invalid skills.sh lock {lock}: missing object field 'skills'.")
            return
        for name in skills:
            if (
                not isinstance(name, str)
                or not name
                or name in {".", ".."}
                or "/" in name
                or "\\" in name
                or Path(name).is_absolute()
            ):
                self.warnings.append(
                    f"Ignored invalid skill name {name!r} in {lock}; expected one path component."
                )
                continue
            if global_lock:
                candidates = [base / "skills" / name for base in global_install_bases]
            else:
                candidates = [
                    lock.parent / agent / "skills" / name
                    for agent in (".agents", ".claude", ".codex")
                ]
            for candidate in candidates:
                if candidate.exists() or candidate.is_symlink():
                    resolved = candidate.resolve(strict=False)
                    self.managed_roots.setdefault(resolved, []).append(
                        f"skill {name!r} recorded in {lock} at {candidate}"
                    )

    def _walk_named_file(self, base: Path, filename: str) -> Iterator[Path]:
        visited: set[Path] = set()

        def on_error(error: OSError) -> None:
            self.warnings.append(
                f"Could not inspect directory while locating {filename}: {error}"
            )

        for directory, names, files in os.walk(
            base, followlinks=True, onerror=on_error
        ):
            current = Path(directory)
            canonical = current.resolve(strict=False)
            if canonical in visited:
                names[:] = []
                continue
            visited.add(canonical)
            names[:] = [
                name
                for name in names
                if name not in {".git", "node_modules", "build", "dist", "vendor"}
                and not self.exclusion(current / name)
            ]
            if filename in files:
                yield current / filename

    def _load_plugin_source_manifests(self) -> None:
        seen: set[Path] = set()
        for scan_root in self.scan_roots:
            base = scan_root if scan_root.is_dir() else scan_root.parent
            for directory in (base, *base.parents):
                for relative in (
                    Path(".claude-plugin/plugin.json"),
                    Path(".codex-plugin/plugin.json"),
                ):
                    manifest = directory / relative
                    canonical = manifest.resolve(strict=False)
                    if canonical in seen or not manifest.is_file():
                        continue
                    seen.add(canonical)
                    self._record_plugin_manifest(directory, manifest)
            if base.is_dir():
                for manifest in self._walk_manifests(base):
                    canonical = manifest.resolve(strict=False)
                    if canonical in seen:
                        continue
                    seen.add(canonical)
                    self._record_plugin_manifest(manifest.parent.parent, manifest)

    def _walk_manifests(self, base: Path) -> Iterator[Path]:
        visited: set[Path] = set()

        def on_error(error: OSError) -> None:
            self.warnings.append(
                f"Could not inspect directory while locating plugin manifests: {error}"
            )

        for directory, names, _files in os.walk(
            base, followlinks=True, onerror=on_error
        ):
            current = Path(directory)
            names[:] = [
                name
                for name in names
                if name not in {".git", "node_modules", "build", "dist", "vendor"}
                and not self.exclusion(current / name)
            ]
            canonical = current.resolve(strict=False)
            if canonical in visited:
                names[:] = []
                continue
            visited.add(canonical)
            if current.name in {".claude-plugin", ".codex-plugin"}:
                manifest = current / "plugin.json"
                if manifest.is_file():
                    yield manifest
                names[:] = []

    def _record_plugin_manifest(self, plugin_root: Path, manifest: Path) -> None:
        self.metadata_paths.add(manifest.resolve(strict=False))
        evidence = f"plugin skill component declared by {manifest}"
        conventional = plugin_root / "skills"
        if conventional.exists():
            self.plugin_source_roots.setdefault(conventional.resolve(), []).append(evidence)
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            self.warnings.append(f"Could not parse plugin manifest {manifest}: {error}")
            return
        if not isinstance(data, dict):
            return
        declared = data.get("skills")
        components = data.get("components")
        if declared is None and isinstance(components, dict):
            declared = components.get("skills")
        for raw in _strings(declared):
            if "://" in raw:
                continue
            target = (plugin_root / raw).resolve(strict=False)
            plugin_canonical = plugin_root.resolve(strict=False)
            if target == plugin_canonical or not _is_within(target, plugin_canonical):
                self.warnings.append(
                    f"Ignored plugin skill component {raw!r} in {manifest}; "
                    "the component must be below the plugin root."
                )
                continue
            component = target.parent if target.name == "SKILL.md" else target
            if component.exists():
                self.plugin_source_roots.setdefault(component, []).append(evidence)
