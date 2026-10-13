# Stage guidance

## Define and dispatch

Extract problem, challenge axes, profile/domain, seed sources, existing ideas, target
contribution, data/code/hardware/time constraints, exclusions, cutoff, language and output
directory. Keep a user's idea separate from evidence that its motivating problem exists.
For audit, start from that idea but still check the underlying gap. Success is a clear
research decision, including “first measure whether this failure exists.”

Orchestrator owns state and evidence IDs. In native mode it delegates retrieval; in
serial mode it explicitly switches research functions and records lack of isolation.
A handoff contains the brief, relevant ledger IDs, narrow questions, resource limits,
input hashes and permitted output location. Workers return files to a single merger.

## Gap finder: same-problem retrieval

Search by task, setting, assumptions and mechanism, then vary terminology. Record both
successful and failed queries with filters, timestamps and actual tools/databases. Use
counterexamples and near-matches; keyword mismatch is not evidence of novelty.
For each retained gap identify what current mechanisms solve, a located limitation,
the nearest methods, why they do not resolve this setting, why this matters and the
observation that would close the gap. At most two per axis; justify a single near-miss.

Distinguish “not reported,” “not established,” “failed in this setting,” and “cannot do.”
An absent ablation does not establish a missing capability. Mark speculative gaps
hypothetical and give a cheap diagnostic. Do not start assembling modules yet.

## Paper reader: goal-directed evidence

Before reading, write the question to resolve. Retrieve the relevant primary text and
record version/date, sections/pages/equations/figures viewed and access limitations.
A digest should answer that question, separate author assertions from empirical support,
code observations and our inference, and link every answer to ledger entries.
If a figure is decisive, actually inspect it; failed extraction is not permission to guess.
A digest can be cumulative but must preserve source and scope for each answer.
Use an isolated reader when available; do not flood every role with full text.

## Innovator: transfer a mechanism

Begin with a few distinct intuitions based on supported gaps. Search other problems
for a mechanism that addresses the same structural difficulty. Each transfer card
records source problem, mechanism, why it works, target problem, shared structure,
required changes, assumptions, difference from the nearest target-domain method,
and likely failure. Name-dropping, replacing task labels and juxtaposing fashionable
modules do not establish transfer. Same-domain inspiration is acceptable when it
requires consequential adaptation; do not fabricate distant inspiration.

Check plausibility of the intuition and necessary assumptions before adding architecture,
notation or hyperparameters. Resource estimates need a cited measurement, a transparent
calculation or an explicit unknown; never invent a GPU configuration.

## Writer: test the explanation

Use the selected candidate's gap and the reviewer’s hardest objection. Write problem,
failure case, core hypothesis, existing-method boundaries, one-sentence contribution,
mechanism, minimal implementation, limitations and evidence links. Claim IDs in the
proposal point to all factual assertions and inferences it depends on; transfer cards
and reviews point to the same ledger rather than inventing new references.

Design the cheapest diagnostic that separates the hypothesis from a simpler account.
Then specify an intervention/negative control, simple alternative, strong baseline,
ablations, metrics and falsification. Distinguish higher scores from evidence that the
claimed mechanism caused improvement. Give conditions to abandon the idea, and
resource estimate assumptions. Only plan a full evaluation when the diagnostic justifies it.
All proposed outcomes remain predictions; the artifact tool never executes experiments.

For all-rejected runs preserve candidate/review records, select no candidate, and report
useful observations and next diagnostics. A concise refusal to claim innovation is valid.
