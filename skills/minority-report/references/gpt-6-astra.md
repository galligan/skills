# GPT-6 Astra review profile

Adapted from [OpenAI's September 11, 2026 guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), checked September 12, 2026. Apply the evidence rules in [model-review.md](model-review.md); the article supplies review hypotheses, not automatic findings.

- Check whether skill descriptions select the actual task or attract unrelated topic mentions. Review overlapping triggers together.
- Check whether entrypoints load only relevant references. A workflow router should expose enough information to choose the next resource without loading every branch.
- Distinguish a useful outcome and verification contract from a fixed itinerary for judgment work. Preserve exact procedures when operations require them.
- Inspect repeated testing demands for redundant work. Preserve checks that establish a distinct property or protect an operational boundary.
- Examine whether approval language stops already-authorized preparation or whether completion criteria stop the agent at a first implementation. Clarify intended scope and completion without expanding authority.

Do not apply an Astra-specific simplification to other consumers without checking their needs. Recheck provider guidance when the target changes.
