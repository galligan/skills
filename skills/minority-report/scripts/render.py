"""Render the complete consolidated audit as Markdown; '-' writes to stdout."""

import argparse
import collections
import json
import re
from pathlib import Path

from validate import read_json, schema_errors


def fence(text, language):
    delimiter = "`" * max(3, max((len(m) + 1 for m in re.findall(r"`{3,}", text)), default=3))
    return f"{delimiter}{language}\n{text}\n{delimiter}"


def inline(text):
    return re.sub(r"([\\`*_{}\[\]<>#|])", r"\\\1", text).replace("\n", " ")


def rank(finding):
    return ({"critical": 0, "high": 1, "medium": 2, "low": 3}[finding["severity"]],
            {"high": 0, "medium": 1, "low": 2}[finding["improvement"]["level"]],
            {"pervasive": 0, "common": 1, "occasional": 2}[finding["reach"]],
            {"high": 0, "medium": 1, "low": 2}[finding["confidence"]], finding["id"])


def render_ownership(scope):
    lines = ["## Ownership signals", ""]
    context = scope.get("ownership_context")
    if context:
        user = (context.get("user") or {}).get("login") or "unavailable"
        organization_context = context.get("organizations", {})
        organizations = ", ".join(organization_context.get("logins", [])) or "none visible"
        lines.extend([
            f"Affiliation check: **{inline(context['status'])}** · Host: {inline(context['host'])} · "
            f"User: {inline(user)} · Organizations ({inline(organization_context.get('status', 'unknown'))}): "
            f"{inline(organizations)}.",
            "",
            inline(context["reason"]),
            "",
        ])
    relevant = []
    for record in scope.get("files", []):
        ownership = record.get("ownership")
        if ownership and ownership.get("repository_affiliation") in {
            "has_external_remote",
            "unknown",
        }:
            relevant.append((record["path"], ownership))
    if not relevant:
        message = (
            "No flagged or unknown files."
            if context
            else "No ownership signals were recorded in this discovery map."
        )
        lines.extend([message, ""])
        return lines
    lines.extend([
        "These are advisory Git-remote affiliation signals, not proof of who authored a file. "
        "All listed files remain in the audit.",
        "",
    ])
    for path, ownership in sorted(relevant):
        details = []
        if ownership.get("repository"):
            details.append("repository " + inline(ownership["repository"]))
        possible = ownership.get("possible_external_source")
        details.append(
            "possible external source "
            + ("yes" if possible is True else "no" if possible is False else "unknown")
        )
        remotes = ownership.get("remotes", [])
        if remotes:
            details.append(
                "GitHub remotes "
                + ", ".join(
                    f"{inline(remote['name'])}: {inline(remote['repository'])} at {inline(remote['url'])} — "
                    f"owner {inline(remote['owner']['login'])} ({inline(remote['owner']['relationship'])})"
                    for remote in remotes
                )
            )
        suffix = (" " + "; ".join(details) + ".") if details else ""
        lines.append(
            f"- {inline(path)} — **{inline(ownership['repository_affiliation'])}**: "
            f"{inline(ownership['reason'])}{suffix}"
        )
    lines.append("")
    return lines


def render(data):
    findings = data["findings"]
    decisions = sum(f["decision_required"] for f in findings)
    routine = len(findings) - decisions
    lines = ["# The Agent’s Minority Report", "", f"{len(findings)} accepted finding{'s' if len(findings) != 1 else ''}: "
             f"{routine} routine proposal{'s' if routine != 1 else ''} and {decisions} decision{'s' if decisions != 1 else ''}.", "",
             "Rankings describe potential consequences and expected improvement, not measured savings. "
             "No proposed source changes have been applied. Diffs are independent proposals; reconcile overlapping alternatives before applying them.", ""]
    for is_decision, title in [(False, "Routine proposals"), (True, "Decisions: safety, authority, and verification")]:
        lines.extend(["# " + title, ""])
        groups = collections.defaultdict(list)
        for finding in findings:
            if finding["decision_required"] == is_decision:
                groups[finding["project"]].append(finding)
        if not groups:
            lines.extend(["No findings in this section.", ""])
        for project, items in sorted(groups.items(), key=lambda x: x[0].casefold()):
            lines.extend(["## " + inline(project), ""])
            files = collections.defaultdict(list)
            for finding in items:
                files[finding["evidence"]["file"]].append(finding)
            for path, entries in sorted(files.items()):
                lines.extend(["### " + inline(path), ""])
                for f in sorted(entries, key=rank):
                    lines.extend([f"**{inline(f['id'])} — {inline(f['title'])}**", "",
                                  f"Severity: **{f['severity']}** · Improvement: **{f['improvement']['level']}** · "
                                  f"Reach: {f['reach']} · Confidence: {f['confidence']} · Category: `{f['category']}`", "",
                                  "**Severity rationale.** " + f["severity_reason"], "",
                                  "**Expected improvement.** " + f["improvement"]["reason"] + " Areas: " + ", ".join(f["improvement"]["areas"]) + ".", "",
                                  "**Confidence rationale.** " + f["confidence_reason"], ""])
                    for index, e in enumerate([f["evidence"], *f["related_evidence"]]):
                        label = "Original instruction" if index == 0 else "Related evidence"
                        lines.extend([f"{label}: {inline(e['file'])}, lines **{e['line_start']}–{e['line_end']}**.", ""])
                        if e.get("source_url"):
                            lines.extend(["Source URL: " + e["source_url"], ""])
                        lines.extend([fence(e["quote"], "text"), ""])
                    lines.extend(["**Potential impact.** " + f["impact"], "", "**Smallest change.** " + f["smallest_change"], "", fence(f["diff"], "diff"), ""])
                    if f["related_findings"]:
                        lines.extend(["Related findings: " + ", ".join(map(inline, f["related_findings"])), ""])
                    if is_decision:
                        lines.extend(["**Decision required.** " + f["decision_reason"], ""])
                    lines.extend(["---", ""])
    lines.extend(["# Coverage and limits", "", ", ".join(f"{key}: {value}" for key, value in sorted(data["coverage_summary"].items())), ""])
    for c in data["coverage"]:
        lines.append(f"- {inline(c['path'])} — **{c['status']}**: {inline(c['reason'])}")
    lines.append("")
    lines.extend(render_ownership(data["scope"]))
    lines.extend(["## Excluded content", ""])
    for e in data["scope"].get("excluded", []):
        lines.append(f"- {inline(e['path'])}: {inline(e['reason'])}")
    lines.extend(["", "## Excluded findings", ""])
    for e in data["excluded_findings"]:
        lines.append(f"- {inline(e['finding']['id'])}: {inline(e['reason'])}")
    lines.extend(["", "## Unresolved references and uncertainty", ""])
    lines.extend(["- " + inline(x) for x in data["unresolved"]] or ["None recorded."])
    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("findings")
    parser.add_argument("--output", default="-", help="Markdown destination or '-' for thread/stdout")
    args = parser.parse_args()
    try:
        data = read_json(args.findings)
        errors = schema_errors(data, "consolidated")
        if errors:
            raise ValueError("\n".join(errors))
        output = render(data)
        if args.output == "-":
            print(output, end="")
        else:
            target = Path(args.output)
            protected = {Path(args.findings).resolve(), *(Path(x["path"]).resolve() for x in data["scope"]["files"])}
            if target.resolve() in protected:
                raise ValueError("Output must not overwrite the consolidated JSON or an audited source")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(output, encoding="utf-8")
            print(json.dumps({"path": str(target.resolve()), "findings": len(data["findings"])}))
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        parser.exit(1, f"Rendering failed: {error}\n")


if __name__ == "__main__":
    main()
