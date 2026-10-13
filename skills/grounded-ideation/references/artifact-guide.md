# Artifact CLI contract

Run with Python 3.10+ and the skill-local requirements.txt. All commands are offline;
there is no model/API client. Resolve SCRIPT to this skill's scripts/research_artifacts.py.

```sh
python "$SCRIPT" init --workspace runs --run-id study --brief brief.json
python "$SCRIPT" update --run runs/study --input update.json
python "$SCRIPT" validate --run runs/study
python "$SCRIPT" audit --run runs/study --require-recommendable
python "$SCRIPT" render --run runs/study
python "$SCRIPT" resume --run runs/study
```

Init also accepts --task, --depth, --literature-mode, --profile, --cutoff YYYY-MM-DD.
Default local-only is conservative; change mode after actual capability probing.
It refuses an existing run. Flags do not configure host tools. `brief.output_directory`
is descriptive; --workspace is the only authority for the output location.

An update is an object with `artifacts` (filename → complete JSON value) and optional
`run` fields. JSONL values are arrays, not strings. Allowed filenames are brief.json,
search-log.jsonl, sources.jsonl, claims.jsonl, gaps.json, candidates.json, reviews.json,
proposal.json. Allowed run fields: config, capabilities, execution, budget, status,
stop_reason. Supply entire nested objects; schemas are under assets/schemas. The
[small update template](../assets/templates/update.json) demonstrates a valid diagnostic stop.
For a complete filled serialization example, inspect
[synthetic-rejection.json](../assets/templates/synthetic-rejection.json). It is explicitly
synthetic test data; never reuse its assertions as real evidence.
Each updated stage is marked complete as a recording operation; it is not a scientific
approval. Changed upstream data invalidates dependent stage status and selections.
Supply freshly rechecked downstream artifacts in the same update, or update them later.

Budget limits are configurable before work; count searches (including failures), reads,
retained candidates and peak concurrency. Search and candidate counts are lower-bounded
by their logged artifacts; reads/concurrency require accurate host records. Revision
limits apply to each candidate. Do not silently raise caps to evade stopping.
Use status=stopped plus stop_reason such as budget_exhausted, search_saturated,
all_rejected or insufficient_evidence. Zero remaining budget is a valid stop, not an error.

Structured files are authoritative. `validate`/`audit` return separate structure,
recommendation_gate and semantic_truth objects. Exit 0 means valid stored artifacts,
including a no-recommendation run. Exit 1 means malformed/unsafe/inconsistent artifacts.
With --require-recommendable, exit 2 means valid artifacts but blocked recommendation.
A PASS gate means the recorded prerequisites exist, never proof of entailment/novelty.

`render` escapes external content and refuses stale state; repeated rendering requires
--replace. Report headings are English except the Chinese title/self-review label;
research prose follows the brief's language. Do not edit report.md to change conclusions.

`resume` checks versions, control metadata and hashes. Changed constraints, source files,
claims or paper digests invalidate dependent conclusions. Old proposals remain available
as stale records with outcome=pending and no selected IDs. Re-review rather than relabel.
Unknown schema versions require explicit migration; the tool does not guess.

For optional digests/frozen records, the orchestrator may create regular files under
papers/ using the host's safe file tools, then run resume before merging conclusions.
Do this before reviewing dependent candidates. Freeze non-obviousness outputs before
comparison; never edit a frozen file to obtain a better assessment. Such changes invalidate
its hash. The source/claim ledgers hold authoritative evidence links.

All CLI reads/writes reject traversal and symlinks and limit each file to 4 MiB. Writes
use same-directory atomic replacement; a per-run exclusive lock serializes cooperating
CLI readers/writers. Agents write separate packets and only the orchestrator calls update.
A crash can leave a lock or a partially updated group: inspect the lock owner and files,
remove a dead lock manually, then resume/revalidate. There is no unsafe force-unlock flag.
Hashes expose partial multi-file updates; this is not a transactional database or defense
against a hostile process racing filesystem operations. Use a private trusted workspace.
