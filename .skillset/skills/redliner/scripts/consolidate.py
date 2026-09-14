"""Consolidate every accepted finding; retain exclusions, coverage, and limits."""

import argparse
import collections
import copy
import json
from pathlib import Path

from validate import evidence_errors, load_sources, read_json, schema_errors, validate_review


def consolidate(reviews, manifest, adjudication):
    sources, errors = load_sources(manifest)
    for review in reviews:
        errors.extend(validate_review(review, sources, skip_findings=True))
    if errors:
        raise ValueError("\n".join(errors))
    reviewers = [review["reviewer"] for review in reviews]
    if len(set(reviewers)) != len(reviewers):
        raise ValueError("Reviewer names must be unique")
    originals, coverage, unresolved = {}, {}, []
    for review in reviews:
        unresolved.extend(f"{review['reviewer']}: {x}" for x in review["unresolved"])
        for finding in review["findings"]:
            if finding["id"] in originals:
                raise ValueError(f"Duplicate finding ID across reviewers: {finding['id']}")
            originals[finding["id"]] = finding
        for item in review["coverage"]:
            previous = coverage.get(item["path"])
            if previous and (previous["status"], previous.get("canonical")) != (item["status"], item.get("canonical")):
                raise ValueError(f"Resolve conflicting coverage dispositions: {item['path']}")
            if previous:
                previous["reason"] += f"\n{review['reviewer']}: {item['reason']}"
            else:
                coverage[item["path"]] = dict(item, reason=f"{review['reviewer']}: {item['reason']}")
    missing = set(sources) - set(coverage)
    if missing:
        raise ValueError("Mapped files lack coverage: " + ", ".join(sorted(missing)))
    if not isinstance(adjudication, dict) or set(adjudication) - set(originals):
        raise ValueError("Adjudication must be an object keyed by existing finding IDs")
    accepted, excluded = [], []
    for identity, original in originals.items():
        decision = adjudication.get(identity)
        finding = copy.deepcopy(original)
        if decision:
            if not isinstance(decision, dict) or not str(decision.get("reason", "")).strip():
                raise ValueError(f"Adjudication needs a reason: {identity}")
            if decision.get("action") == "exclude":
                if set(decision) != {"action", "reason"}:
                    raise ValueError(f"Unexpected exclusion fields: {identity}")
                excluded.append({"finding": original, "reason": decision["reason"]})
                continue
            if decision.get("action") != "override" or set(decision) != {"action", "reason", "changes"}:
                raise ValueError(f"Invalid adjudication action/fields: {identity}")
            if not isinstance(decision["changes"], dict) or "id" in decision["changes"]:
                raise ValueError(f"Overrides must be objects and preserve IDs: {identity}")
            finding.update(decision["changes"])
        accepted.append(finding)
    for link in manifest.get("links", []):
        if link["status"] in {"missing", "external", "unresolved"}:
            unresolved.append(f"{link['status']} reference from {link['from']}: {link['reference']}")
    unresolved.extend(manifest.get("warnings", []))
    for root in manifest.get("roots", []):
        if root.get("status") not in {"found", "included", "exists", "excluded"}:
            unresolved.append(f"Scope root {root['path']}: {root.get('status', 'unknown')}")
    result = {
        "schema_version": "1.0", "reviewers": reviewers, "scope": manifest,
        "coverage": sorted(coverage.values(), key=lambda x: x["path"]),
        "coverage_summary": dict(collections.Counter(x["status"] for x in coverage.values())),
        "findings": accepted, "excluded_findings": excluded, "adjudication": adjudication,
        "unresolved": list(dict.fromkeys(unresolved)),
    }
    errors = schema_errors(result, "consolidated")
    if not errors:
        for finding in accepted:
            errors.extend(evidence_errors(finding, sources))
            for related in finding["related_findings"]:
                if related not in originals or related == finding["id"]:
                    errors.append(f"Invalid related finding: {finding['id']} -> {related}")
    if errors:
        raise ValueError("\n".join(errors))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reviews", nargs="+")
    parser.add_argument("--map", required=True, dest="manifest")
    parser.add_argument("--output", default="audit/findings.json")
    parser.add_argument("--adjudication", help="JSON exclusions/overrides keyed by finding ID")
    args = parser.parse_args()
    try:
        result = consolidate([read_json(p) for p in args.reviews], read_json(args.manifest),
                             read_json(args.adjudication) if args.adjudication else {})
        output = Path(args.output)
        protected = {Path(p).resolve() for p in [*args.reviews, args.manifest]}
        protected.update(Path(f["path"]).resolve() for f in result["scope"]["files"])
        if args.adjudication:
            protected.add(Path(args.adjudication).resolve())
        if output.resolve() in protected:
            raise ValueError("Output must not overwrite a source, map, review, or adjudication")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"path": str(output.resolve()), "findings": len(result["findings"]),
                          "decisions": sum(f["decision_required"] for f in result["findings"]),
                          "excluded_findings": len(result["excluded_findings"])}))
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        parser.exit(1, f"Consolidation failed: {error}\n")


if __name__ == "__main__":
    main()
