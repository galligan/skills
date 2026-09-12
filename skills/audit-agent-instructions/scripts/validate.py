"""Validate review artifacts and their live evidence without changing sources."""

import argparse
import hashlib
import json
from pathlib import Path

from diffcheck import check_diff

SKILL = Path(__file__).resolve().parent.parent


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def schema_errors(data, kind="review"):
    try:
        from jsonschema import Draft202012Validator
    except ImportError as error:
        raise RuntimeError("Install this skill's requirements.txt in an isolated Python environment") from error
    schema = read_json(SKILL / "references" / f"{kind}.schema.json")
    return [f"{list(e.path)}: {e.message}" for e in Draft202012Validator(schema).iter_errors(data)]


def load_sources(manifest):
    sources, errors = {}, []
    for item in manifest["files"]:
        path = item["path"]
        if not Path(path).is_absolute():
            errors.append(f"Map path must be absolute: {path}")
            continue
        if str(Path(path).resolve()) != path:
            errors.append(f"Map path must be canonical: {path}")
            continue
        if path in sources:
            errors.append(f"Duplicate mapped path: {path}")
            continue
        try:
            raw = Path(path).read_bytes()
            if hashlib.sha256(raw).hexdigest() != item["sha256"]:
                errors.append(f"Source changed since mapping: {path}")
            sources[path] = raw.decode("utf-8")
        except (OSError, UnicodeError) as error:
            errors.append(f"Cannot read mapped source {path}: {error}")
    return sources, errors


def evidence_errors(finding, sources):
    errors = []
    for item in [finding["evidence"], *finding["related_evidence"]]:
        path = item["file"]
        if path not in sources:
            errors.append(f"Unmapped evidence: {path}")
            continue
        lines = sources[path].splitlines()
        start, end = item["line_start"], item["line_end"]
        if end < start or end > len(lines):
            errors.append(f"Invalid inclusive range: {path}:{start}-{end}")
        elif "\n".join(lines[start - 1:end]) != item["quote"]:
            errors.append(f"Quote differs from source: {path}:{start}-{end}")
    if finding["decision_required"] and not finding["decision_reason"].strip():
        errors.append("Decision-required finding needs a reason")
    if finding["category"] in {"redundant_verification", "premature_confirmation"} and not finding["decision_required"]:
        errors.append("Verification/confirmation proposal must be decision-required")
    if finding["category"] == "conflict" and not finding["related_evidence"]:
        errors.append("Conflict needs related evidence for the other instruction")
    try:
        check_diff(finding["diff"], sources, finding["evidence"]["file"])
    except ValueError as error:
        errors.append(str(error))
    return [f"{finding['id']}: {error}" for error in errors]


def validate_review(data, sources, skip_findings=False):
    errors = schema_errors(data)
    if errors:
        return errors
    ids, paths = set(), set()
    for finding in data["findings"]:
        if finding["id"] in ids:
            errors.append(f"Duplicate finding ID: {finding['id']}")
        ids.add(finding["id"])
        if not skip_findings:
            errors.extend(evidence_errors(finding, sources))
    for item in data["coverage"]:
        path = item["path"]
        if path in paths:
            errors.append(f"Duplicate coverage: {path}")
        paths.add(path)
        if path not in sources and item["status"] not in {"missing", "blocked"}:
            errors.append(f"Unmapped coverage: {path}")
        if item["status"] == "duplicate":
            canonical = item.get("canonical")
            if canonical == path or canonical not in sources or sources.get(path) != sources.get(canonical):
                errors.append(f"Duplicate coverage needs an identical mapped canonical source: {path}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review")
    parser.add_argument("--map", required=True, dest="manifest")
    args = parser.parse_args()
    try:
        sources, errors = load_sources(read_json(args.manifest))
        errors.extend(validate_review(read_json(args.review), sources))
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
        return int(bool(errors))
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        parser.exit(1, f"Validation failed: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
