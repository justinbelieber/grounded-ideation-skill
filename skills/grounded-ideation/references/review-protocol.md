# Review and non-obviousness

A reviewer searches the target task and mechanism, including synonyms and likely prior
combinations. Persist an objection supported by located evidence, uncertainty and a
next discriminating test. Use survive/revise/reject/insufficient_evidence. A failed
retrieval, missing full text or parse failure yields insufficient_evidence, not survival.
Link the actual search IDs and claim IDs. Review each candidate revision explicitly.

Record the reviewer identity/tool, actual input artifact list and its hash, whether
history was inherited, and isolation: same-context/separate-context/proposal-blind.
A separate instance of the same model is not independent scientific validation. Do not
call a context blind after it saw the candidate. When isolation is unavailable, say
serial same-context self-review. It may check evidence, but it cannot support blind claims.

Deep mode adds two bounded calls when genuinely isolated contexts are available:

1. Give a context only the target problem and permissible nearest prior work, excluding
   the candidate, its title, target paper, distinctive hints and generation history.
   Ask for concrete operations derivable from those priors, their steps and assumptions.
   Freeze its JSON as an immutable `papers/frozen-<id>.json` with `proposal_seen=false`,
   a nonempty `mechanisms` list and input provenance. Hash it before exposing the proposal.
2. A separate comparison receives the frozen file and candidate. Compare operations and
   identify any consequential additional step. Never repair or extend the frozen mechanisms
   after seeing the candidate. Record the file and SHA-256 in the review. Empty/invalid
   derivation or unavailable isolation is unscored. It does not imply high novelty.

The CLI verifies an existing frozen file/hash and recorded status. The host and evaluator
must establish actual context isolation and freeze timing; hashes alone cannot prove either.
Missing deep evidence blocks a deep recommendation. The user may explicitly choose a
shallower run, recorded as a configuration change; do not silently downgrade to pass.

Revision ceilings are per candidate. Stop at the limit or search saturation even if the
verdict remains revise. No reviewer score is required and no loop seeks a target score.
