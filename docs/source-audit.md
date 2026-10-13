# Source audit

Access date: **2026-10-13 (Asia/Shanghai)**. This is a reading/provenance audit, not a
reproduction or legal clearance. Small source caches were kept outside the deliverable;
no paper, upstream source, data records or weights are redistributed.

| Source | Version / scope actually inspected | Status |
| --- | --- | --- |
| [Paper record](https://arxiv.org/abs/2610.04074) | v1, submitted 2026-10-02; title, author list, version, license link | VERIFIED_ACCESS |
| [Paper HTML](https://arxiv.org/html/2610.04074v1) | §§3–5; Appendix A role permissions and output structures; B training/gates; C evaluation; D construction/leakage; E budgets/cutoff; conclusion. Text/tables inspected; plots not visually evaluated. | VERIFIED_ACCESS; not abstract-only |
| [IdeaScientist repository](https://github.com/jiarui-liu/IdeaScientist) | commit `82a98a08772eab08d11fd097445afa4a8eaaa5b3`, confirmed through commits/main API; recursive tree inspected before choosing paths | VERIFIED_ACCESS |
| [Repository LICENSE](https://github.com/jiarui-liu/IdeaScientist/blob/82a98a08772eab08d11fd097445afa4a8eaaa5b3/LICENSE) | Full file: CC BY-NC 4.0. pyproject metadata agrees. | VERIFIED_ACCESS |
| [Codex Skills](https://developers.openai.com/codex/skills/) | Redirects to [Build skills](https://learn.chatgpt.com/docs/build-skills); manifests, progressive loading, local discovery, metadata and invocation | VERIFIED_ACCESS |
| [Official skill-creator](https://github.com/openai/skills/tree/main/skills/.system/skill-creator) | path's latest commit `4ab6e0fd99c6667163bc34173e3ed3a3fed75ebc`; remote SKILL.md structure/core guidance and Apache-2.0 license inspected | VERIFIED_ACCESS |
| Installed skill-creator | Session-provided SKILL.md read in full; openai_yaml reference read; bundled metadata generator and quick validator executed | VERIFIED_LOCAL; installed prose differs from GitHub version |
| [Svalbard data card](https://huggingface.co/datasets/Jerry999/SvalbardIdeaVault) | card and metadata at revision `64ab36be959afab06066f8c1e7ea292dba9362e5`; splits, license and limitations only | VERIFIED_CARD; records NOT_DOWNLOADED |

## Implementation inspection (same pinned upstream commit)

Paths below are relative to the repository linked above; fetched files were read only,
never executed or imported. “Targeted” means the named logic was inspected, not every line.

| Actual path | Read scope |
| --- | --- |
| `README.md`, `pyproject.toml` | Layout, corpus links, dependencies and license metadata. |
| `ideascientist/harness/orchestrator.py` | Scheduling/role ownership, handoff construction and report completion behavior. |
| `ideascientist/harness/roles.py` | Role definitions and permissions located; prompt text not reused. |
| `ideascientist/harness/tools.py` | Tool caps, permitted files, confined paths and role tool routing, targeted. |
| `ideascientist/rewards/common.py` | ID resolution, seeded citations, citation F1 and validity aggregation, targeted. |
| `ideascientist/rewards/{gap_finder,innovator,report_writer}/reward.py` | Gate definitions, read-before-cite, failure handling, targeted. |
| `ideascientist/evaluation/novelty.py` | Complete implementation, including empty comparison-set refusal. |
| `ideascientist/evaluation/novelty_aspects.py` | Blind derivation inputs, frozen comparison, parsers and aggregation, targeted. |
| `ideascientist/evaluation/citations.py` | Identifier and accessible-cutoff routines located; not exhaustively reviewed. |
| `ideascientist/vault/schema.py`, `decompose.py` | Masking definition, field structure and extraction constraints, targeted. |
| `ideascientist/vault/splits.py` | Candidate selection and version/date limitations; targeted filter implementation. |
| `ideascientist/vault/references/report_writer.py` | Downloaded for audit but only symbol discovery; full implementation UNVERIFIED. |

## Differences and limitations

The paper separates trained producer roles from orchestration, targeted reading and
review. This project keeps only a host-driven inference workflow. It allows a valid
no-proposal stop, adds explicit insufficient-evidence states, and does not implement RL.
Some upstream read-before-cite checks accept seeded artifacts; this implementation keeps
per-claim locations instead. Upstream code also has an optional baseline read-gate bypass;
we do not adopt it. These are intentional departures, not equivalent reproduction.

The data card's published split sizes differ from the paper's described dataset. We do
not reconcile them without records or infer benchmark equivalence. Paper prose and
novelty_aspects distinguish structural transfer from numerical literature similarity;
this project uses neither score as its own factuality measure. No plotted performance
claim is relied on here. Citation/URL checks cannot verify the scientific conclusions.

Initial shell DNS access failed; browser access worked. After session network permission,
read-only downloads succeeded. The data-card web viewer failed, but its raw endpoint
worked. The generic OpenAI skills root LICENSE URL returned 404; skill-creator's own
LICENSE.txt supplied Apache-2.0. No unavailable source is silently treated as verified.

Codex documentation now lists repo `.agents/skills` and user `~/.agents/skills`. The
installed creator's default-path prose differs. The repository documents the current
repo-local path and validates an isolated copy, without modifying global configuration.
