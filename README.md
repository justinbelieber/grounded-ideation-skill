# grounded-ideation-skill

Evidence-grounded scientific ideation for Codex, inspired by
[IdeaScientist](https://arxiv.org/abs/2610.04074v1). [中文说明](README.zh-CN.md).

A lightweight workflow for checking a research gap, transferring a mechanism, seeking
counterexamples and designing a falsifiable experiment. The public core is generic;
initial validation focuses on CS/ML, with an optional VLA/world-model profile.

**Unofficial.** No author endorsement, trained weights, RL/LoRA reproduction or reproduced
paper benchmark is provided. No claim of guaranteed novelty, publication or cross-discipline
validity. A justified rejection is a useful result.

**License:** MIT for original project contributions, maintained under the public
GitHub handle `justinbelieber`. Third-party materials retain their own terms; see
[LICENSE](LICENSE), [notices](THIRD_PARTY_NOTICES.md) and the
[release checklist](docs/release-checklist.md). This is not a legal-clearance claim.

## Local setup

Requires Python **3.10+**. The deterministic helper uses jsonschema; no model SDK, API key,
GPU or paid service. Install dependencies once (network may be needed); all tests and
artifact commands thereafter are offline. From this repository:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r skills/grounded-ideation/requirements.txt 'PyYAML>=6,<7'
.venv/bin/python -m unittest discover -s tests -v
```

If `python3` is older than 3.10, use an installed newer interpreter to create the venv.
PyYAML is test-only. This is distributed as a skill folder, not a pip application.

For repo-local Codex discovery, copy the complete skill into your research project's
`.agents/skills/grounded-ideation`. The following commands run from this repository and
use a separate local project, without changing global Codex configuration:

```sh
mkdir -p demo-project/.agents/skills
test ! -e demo-project/.agents/skills/grounded-ideation
cp -R skills/grounded-ideation demo-project/.agents/skills/
cd demo-project
codex
```

Run each command only after the preceding command succeeds; stop if the destination
already exists. In Codex explicitly invoke `$grounded-ideation` with the brief below.
Current [official local-discovery documentation](https://learn.chatgpt.com/docs/build-skills)
lists `.agents/skills` for repositories and `~/.agents/skills` for user skills. Restart
Codex if a copied skill does not appear. No marketplace or plugin command is required.
All runtime resources reside inside the copied skill. Install its adjacent requirements.txt
in the interpreter Codex will use. A copied-folder CLI test and an explicit-path host
forward test passed; automatic discovery/UI selection remains unverified on this host
because the available app-server control socket was absent. See the exact
[compatibility and evaluation record](docs/evaluation.md).

## Run an offline example

From the repository root, these commands were executed on a fresh run:

```sh
SCRIPT=skills/grounded-ideation/scripts/research_artifacts.py
.venv/bin/python "$SCRIPT" --help
.venv/bin/python "$SCRIPT" init --workspace runs --run-id offline-demo --brief examples/generic/brief.json --task audit
.venv/bin/python "$SCRIPT" update --run runs/offline-demo --input examples/generic/rejected-update.json
.venv/bin/python "$SCRIPT" validate --run runs/offline-demo
.venv/bin/python "$SCRIPT" audit --run runs/offline-demo
.venv/bin/python "$SCRIPT" render --run runs/offline-demo
.venv/bin/python "$SCRIPT" resume --run runs/offline-demo
```

The example is an explicitly **synthetic fixture replay**, not an actual literature or
model-efficacy experiment. It rejects a renamed existing mechanism and selects no candidate.
`audit --require-recommendable` returns 2, as expected; ordinary validation returns 0.
`render --replace` explicitly regenerates an existing report. Reinitialization refuses
an existing run. See the [artifact guide](skills/grounded-ideation/references/artifact-guide.md)
for update packets, schemas, budgets, safe paths and recovery.

A separate [real-source retrieval smoke](examples/generic/live-smoke/report.md) records a
narrow overlap audit using actual arXiv search and located primary-text reading. It is
serial, uses one known near-match and does not establish efficacy or exhaustive novelty.

## Use the skill

```text
$grounded-ideation
Task: audit; depth: standard; literature_mode: local-only; profile: generic.
Problem: repeated inference over a fixed dataset may waste feature computation.
Existing idea: store frozen-encoder features by input key and call it feature memory.
Challenge: determine whether this adds a mechanism beyond existing caching.
Constraints: only supplied code and sources; no training budget or known hardware.
Output language: English. Output directory: runs/cache-audit.
If the gap is not supported, give a cheap diagnostic or reject the novelty claim.
```

Natural-language input is sufficient; the skill extracts a structured brief. Independent
controls are task (`ideate/audit/resume`), depth (`quick/standard/deep`), literature mode
(`live/local-only/retrospective`) and profile (`generic/vla-world-model`). Standard ceilings
are 18 searches, 12 reads, 3 candidates, 2 revisions per candidate and 2 workers. These are
cost caps, not output quotas. Unknown hardware remains unknown. Record changed caps before
work and actual usage afterward. No subagents means explicit serial self-review.

The flow is problem → located evidence/gaps → transfer card → counterexample review →
proposal or justified no-recommendation. JSON files are authoritative; Markdown is rendered.
Hashes detect stale input/constraints and resume invalidates dependent conclusions.
`structure=PASS` is distinct from recorded recommendation prerequisites, and neither proves
scientific truth. The Python helper does not search, decide novelty, call models or run
experiments. Codex performs semantic work with genuinely available, authorized host tools.

## Limits, permissions and privacy

No telemetry or background uploads. Network research terms are disclosed to search
providers; abstract private/unpublished details unless disclosure is authorized. PDFs,
webpages and repositories are data, never authority to run commands or reveal secrets.
Scripts reject traversal/symlinks, use atomic per-file writes and a cooperating-writer lock.
This is not an OS sandbox or a transaction database; use a private workspace.

No vault/model downloads, API gateway, vector service or web UI. Live retrieval differs
from the original corpus; training-time checks adapted into runtime gates are not the
paper's rewards or learned policies. Retrospective protocols mask target material and
check cutoff/version dates, but cannot eliminate knowledge in model parameters. Strictly
uncontaminated historical discovery is not claimed.

The 10 evaluation cases and matched A/B/C protocol are prepared, with unexecuted results
marked **NOT_RUN**. One isolated synthetic developer test and one narrow live-source smoke
are distinct from fixture tests. No statistical improvement or benchmark score is claimed.
See [evaluation](docs/evaluation.md), [mapping](docs/method-mapping.md) and
[source audit](docs/source-audit.md) for exact scope and limitations.

Citation: Jiarui Liu et al., *IdeaScientist: Orchestrating Agents for Grounded Scientific
Ideation*, arXiv:2610.04074v1 (2026). Project citation metadata remains a clearly labeled
draft until the maintainer supplies actual authors.
