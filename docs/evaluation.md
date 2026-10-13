# Validation and evaluation record

Executed 2026-10-13, Python 3.12.14 on macOS. Engineering correctness, host behavior and
scientific effectiveness are separate. No performance/acceptance/novelty guarantee.

| Check | Actual result | Scope |
| --- | --- | --- |
| Installed skill-creator quick_validate.py | PASS | Frontmatter/name/scaffold format; not host discovery |
| Metadata generator | PASS | Supported interface fields; no fake multi-agent configuration |
| Offline unit/integration tests | 30 PASS | Schemas, references, hashes, cutoff/version, safe paths, state, failures, locks, render, copied install, staged-byte audit |
| README CLI sequence | PASS; expected exit 2 for --require-recommendable | Commands/stdout in command-results.json |
| Isolated installed-copy helper | PASS | Only copied skill resources plus declared dependency needed |
| Independent-context synthetic forward test | COMPLETED, justified rejection | Explicit SKILL.md loading, no inherited parent turns |
| Narrow real-source smoke | COMPLETED, overlap rejected | Actual search and located arXiv reading; one source; serial review |
| Automatic Codex discovery/UI selection | UNVERIFIED | app-server proxy attempted; control socket absent |
| Hosted GitHub CI / Python 3.10 and 3.13 | NOT_RUN | Only local Python 3.12 tested |
| Full A/B/C scientific comparison | NOT_RUN | 10 cases and matched protocol prepared |
| Blind deep non-obviousness evaluation | NOT_RUN | Recorded-state gates tested; no independent scientific assessment |
| Real VLA / cross-discipline efficacy | NOT_RUN | Optional profile and synthetic brief only |
| CFF release validation / legal clearance | NOT_RUN / pending | Project authors and license unresolved |

## Engineering evidence

Executed commands, with portable paths instead of private machine paths:

```sh
python -m unittest discover -s tests -v
python <installed-skill-creator>/scripts/quick_validate.py skills/grounded-ideation
python <installed-skill-creator>/scripts/generate_openai_yaml.py skills/grounded-ideation --interface ...
```

[command-results.json](command-results.json) contains the exact README helper commands
and outputs. Fresh initialization, update, validate, audit, render and resume returned 0.
The valid rejected run returns 2 only when recommendation eligibility is requested.
Semantic truth remains NOT_AUTOMATICALLY_VERIFIED even when structure passes.

Tests cover missing citations, unverified/synthetic evidence, abstract-only misrepresented
as full text, publication/revision cutoff, new measured results in unexecuted proposals,
all-rejected output, reviewer/tool failure, bounded stops, inert external-text rendering,
traversal, symlinks, duplicate IDs, stale constraints/evidence, version mismatch, shared
writer lock and installed-copy independence. Contradictory survival state and empty blind
derivation are blocked. Semantic renaming/analogy judgments are not established by these
string/schema tests. The release-scanner test checks ignored-but-staged sensitive text,
including a clean working copy with sensitive bytes still in the Git index.
A usage-only budget update preserves a completed decision; constraint-limit changes
invalidate it. The exported pilot normalizes its Python executable path for privacy and
refreshes the control hash; research artifacts and their hashes are unchanged.

## Developer pilot and one revision

The evaluator received only a skill copy, brief and synthetic raw corpus in a separate
workspace. It received no intended verdict, bug hints, parent conclusions or other
condition outputs. It used 11 shell-tool interactions, 8 CLI invocations, 2 local corpus
queries, 1 corpus read, 1 candidate, 0 revisions and peak research concurrency 1.
Tokens/billing: NOT_AVAILABLE. No paid API service was launched. Raw outputs are in
examples/generic/forward-test; [pilot-summary.json](pilot-summary.json) records counts.

It rejected the renamed caching idea, selected no candidate and retained an unexecuted
diagnostic. Corpus injection was ignored. Validate/audit/render succeeded; the
recommendation-required audit returned expected exit 2. This is one developer case with
serial self-review inside the evaluator, not independent scientific review or a matched
baseline trial. It is related to dev/01, not a heldout result.

Observed usability problems led to one scoped revision: add a complete installed synthetic
update template, render list values readably, and clarify synthetic gate messages.
Re-rendering the saved pilot checked the display fix, and regression tests were rerun.
No second model result is implied. A separate authoring smoke exposed relative-path
handling in the Python helper API; paths were normalized and the smoke then passed.

## Real retrieval smoke

[Live report](../examples/generic/live-smoke/report.md): one targeted web query for
IdeaScientist, verified arXiv metadata and located §3.1/A.1 reading. Irrelevant results
were logged and excluded. The source was read during the source audit; that evidence was
transparently reused. Structured artifacts were assembled afterward in the authoring
session. Counts: 1 query, 1 targeted paper read, 1 candidate, 0 revisions, serial review.
This establishes real tool access and traceability, not broad novelty coverage or
comparative efficacy. No experiment was executed or performance measured.

## Compatibility

Local CLI version: `0.162.0-alpha.17.2`. Its actual --help and generated protocol schemas
were inspected before attempting app-server proxy initialize/skills-list. The proxy could
not connect because its control socket was absent. No successful discovery response or
UI invocation is claimed. The independent host subagent did read the installed SKILL.md
by explicit path and complete a run. The copied skill's CLI also worked outside the repo.
No global configuration, model override, marketplace manifest or unsupported agent field
was introduced. CLI startup emitted a PATH-alias permission warning; it did not affect
format tests or helper commands.

## Future comparison

Six development and four execution-heldout tasks are in evals/cases; hashes are frozen in
case-manifest.json. All A/B/C cells remain NOT_RUN. Task authors saw the prompts; these
are not a secret independent benchmark. A maintainer should prepare sealed evaluator
answers and a fresh holdout before making scientific claims. Never reuse tuned test
outcomes as unseen evidence.

A is a strong evidence-aware single pass outside this repository, without the skill,
AGENTS.md or generated artifacts. B uses stages but disables cross-problem mechanism
retrieval. C uses the full skill. Match model, brief, corpus, tools and caps, isolate
conditions, and report actual usage. Fixed-corpus and live retrieval studies are separate.
Follow evals/baseline-prompts.md and evals/rubric.md. Report existence/support, near-matches,
mechanism changes, constraints, experiments and completion/refusal/failure separately.
Citation F1 is not factuality. Judges are auxiliary to human review; no small-sample
statistical claim or invented example performance figure is reported.
