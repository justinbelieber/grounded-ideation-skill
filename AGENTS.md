# Repository development

This is an unofficial scientific ideation skill, not a trained model or agent platform.
Keep runtime resources inside skills/grounded-ideation. Run offline unit/integration
tests with `python -m unittest discover -s tests -v` after code changes. Use Python 3.10+.
Keep schema and cross-file integrity validation separate from semantic judgments.

Use synthetic- identifiers for fixtures. Never fabricate literature or performance.
Do not read heldout task outcomes while tuning development behavior. Baseline condition
A must execute outside this repository and without these instructions or the skill.
No recursive model runs or network-dependent CI tests. No private artifacts in commits.

Inspect file provenance before changing license notices. Publication requires the
maintainer confirmations in docs/release-state.json and the release checklist. Do not
infer authorization for a public remote, push, global configuration or billing changes.
