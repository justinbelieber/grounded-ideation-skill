# Method mapping

Source locators: [paper v1](https://arxiv.org/html/2610.04074v1) and the pinned
[upstream implementation](https://github.com/jiarui-liu/IdeaScientist/tree/82a98a08772eab08d11fd097445afa4a8eaaa5b3).
Runtime paths below start at `skills/grounded-ideation/`. All code and prose here were
written independently for this project; this table is not a license determination.

| Original locator → intent | Local implementation | Treatment / deviation and limit | Verification |
| --- | --- | --- | --- |
| §3.1, A.1 → specialize roles | SKILL.md; references/workflow.md | Adapt: native tools if available, explicit serial fallback | Developer forward test; isolation recorded |
| A.1 → same-problem retrieval | workflow.md, search-log schema | Preserve distinction; live/local retrieval replaces vault | Search regime and near-miss ledger |
| A.1 → cross-problem mechanisms | workflow.md; candidate transfer schema | Adapt to bounded purposeful retrieval, no domain quota | Semantic surface-transfer case |
| A.1, Table 7 → targeted reading | evidence-policy.md; source/claim schemas | Preserve source locations; host-specific reader | Abstract/full-text regression |
| A.2 → shared stage artifacts | scripts/research_artifacts.py | Adapt: JSON authority, single merger, hashes | Update/render/resume integration |
| Table 6 → iterative challenge | review-protocol.md | Adapt: add insufficient_evidence and bounded revisions | Reviewer failure regression |
| B.1, rewards/* → validity gates | schemas; structure(), quality() | Adapt training checks into runtime prerequisites | ID/evidence/cutoff tests; no truth claim |
| Table 5; vault/schema.py → outcome masking | proposal schema; result_origin checks | Adapt: never measured new results; prior-work results allowed outside masked eval | Results-origin regression; semantic eval still needed |
| E.2; vault/splits.py → temporal retrieval | source dates; evaluation-protocol.md | Adapt: check accessed version dates too; model memory uncontrolled | Cutoff/version tests |
| C; evaluation/novelty_aspects.py → structural transfer | transfer card; rubric.md | Adapt: require actual operation and adaptation; no imported score | Surface-analogy case NOT_RUN |
| C → proposal-blind derivation | review-protocol.md; frozen hash check | Adapt: unscored if isolation/derivation fails | Recorded-state tests; true blind eval NOT_RUN |
| §3.2, B → role training | Explicit exclusion | Not implemented: no RL, LoRA, rewards or learned policies | Dependency/source inventory |
| §5.3 → ablate components | evals/baseline-prompts.md | Adapt: matched A/B/C, B removes cross-problem search | Full comparison NOT_RUN |

A runtime gate is not the original reward function and does not imply a learned policy.
Live search is not equivalent to the original corpus. Logical/file permissions do not
provide an OS sandbox. JSON integrity is engineering evidence, not scientific validity.
