"""Check proposed unified diffs in memory; never write audited files."""

import re
from pathlib import Path

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?:.*)$")


def resolve_header(header, sources, primary):
    name = header.split("\t", 1)[0]
    if name == "/dev/null":
        return None
    if name.startswith(("a/", "b/")):
        name = name[2:]
    path = Path(name)
    if path.is_absolute():
        resolved = str(path.resolve())
        if resolved in sources:
            return resolved
    else:
        candidates = [p for p in sources if Path(p).as_posix().endswith("/" + name)]
        if primary in candidates:
            return primary
        if len(candidates) == 1:
            return candidates[0]
    raise ValueError(f"Diff target is unmapped or ambiguous: {name}")


def check_diff(diff, sources, primary):
    """Validate line counts, source context, and hunk positions independently."""
    lines = diff.splitlines()
    i = 0
    seen = set()
    changed = False
    while i < len(lines):
        if lines[i].startswith(("diff --git ", "index ")) or not lines[i]:
            i += 1
            continue
        if not lines[i].startswith("--- "):
            raise ValueError(f"Expected --- file header at diff line {i + 1}")
        old_name = lines[i][4:]
        i += 1
        if i >= len(lines) or not lines[i].startswith("+++ "):
            raise ValueError("Missing +++ file header")
        new_name = lines[i][4:]
        i += 1
        old_path = resolve_header(old_name, sources, primary)
        # New documents are proposals only, with an explicit absolute destination.
        if old_path is None:
            destination = new_name[2:] if new_name.startswith("b/") else new_name
            if not Path(destination).is_absolute() or Path(destination).exists():
                raise ValueError("New-file diff needs an absent absolute destination")
            new_path = destination
        else:
            new_path = resolve_header(new_name, sources, primary)
        if old_path and new_path and old_path != new_path:
            raise ValueError("Use separate delete/add proposals for file renames")
        identity = old_path or new_path
        if identity in seen:
            raise ValueError(f"Repeated file section: {identity}")
        seen.add(identity)
        original = sources[old_path].splitlines() if old_path else []
        previous_end = offset = hunks = 0
        while i < len(lines) and not lines[i].startswith(("--- ", "diff --git ")):
            if not lines[i]:
                i += 1
                continue
            match = HUNK.match(lines[i])
            if not match:
                raise ValueError(f"Invalid hunk header at diff line {i + 1}")
            old_start, old_count, new_start, new_count = (
                int(match[1]), int(match[2] or 1), int(match[3]), int(match[4] or 1)
            )
            position = old_start - 1 if old_count else old_start
            new_position = new_start - 1 if new_count else new_start
            if position < previous_end or position > len(original):
                raise ValueError("Overlapping or out-of-range hunk")
            if new_position != position + offset:
                raise ValueError("New hunk position disagrees with preceding changes")
            i += 1
            before, after = [], []
            previous_line = None

            def check_eof_marker():
                if previous_line is None:
                    raise ValueError("Newline marker has no preceding hunk line")
                if previous_line[0] != "+" and (
                    position + len(before) != len(original)
                    or sources.get(old_path, "").endswith(("\n", "\r"))
                ):
                    raise ValueError("Newline marker disagrees with the original source")

            while len(before) < old_count or len(after) < new_count:
                if i >= len(lines):
                    raise ValueError("Truncated hunk")
                line = lines[i]
                i += 1
                if line == "\\ No newline at end of file":
                    check_eof_marker()
                    continue
                if not line or line[0] not in " +-":
                    raise ValueError("Hunk lines must start with space, +, or -")
                if line[0] != "+":
                    before.append(line[1:])
                if line[0] != "-":
                    after.append(line[1:])
                if line[0] in "+-":
                    changed = True
                previous_line = line
                if len(before) > old_count or len(after) > new_count:
                    raise ValueError("Hunk counts disagree with its content")
            if i < len(lines) and lines[i] == "\\ No newline at end of file":
                check_eof_marker()
                i += 1
            if original[position:position + old_count] != before:
                raise ValueError(f"Hunk source context differs: {identity}:{old_start}")
            previous_end = position + old_count
            offset += new_count - old_count
            hunks += 1
        if not hunks:
            raise ValueError("File section has no hunks")
        if new_path is None and len(original) + offset != 0:
            raise ValueError("Deletion diff does not remove the full file")
    if not seen or not changed:
        raise ValueError("Diff contains no proposed change")
