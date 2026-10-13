# Evaluation rubric

These criteria require semantic inspection; string matching is not a substitute.
Blind evaluators to condition and randomize display order. Preserve raw outputs and
adjudications. Human-review hallucination, decisive prior-work and recommendation samples.

| Measure | Record and denominator |
| --- | --- |
| Source existence | Verified real sources / claimed real sources; report unknown and fabricated separately. |
| Evidence support | Supported key fact claims / all key fact claims; inspect original located passages. |
| Decisive near-match | Whether the work that defeats a claimed novelty was identified and its mechanism compared. |
| Mechanism difference | Concrete operation/assumption changes; do not reward renamed modules or metaphors. |
| Transfer | Source mechanism, common structure and necessary adaptation; unsupported cases remain unscored. |
| Constraints | Satisfied / violated / unknown for each resource, privacy and cutoff constraint. |
| Experiment | Executable intervention, baseline, alternative explanation, negative control and refutation condition. |
| Outcome | Valid completion, justified refusal, or failed/incomplete; all tasks stay in the denominator. |
| Cost | Actual tool counts/turns, tokens/time and available billing; NOT_AVAILABLE when hidden. |

Do not combine these into one number that hides hallucination. Structural check results
are a separate table. Compare matched cases, report counts and individual failures for
small samples. Multiple runs and uncertainty intervals require an adequate preregistered
sample; this repository reports no invented performance figures.

For development use, inspect failures then make one scoped revision and rerun regression.
Freeze heldout protocol/corpus/model/budget before running it. Never tune on its outcomes
and reuse that same set as an untouched efficacy estimate. Current heldout tasks are
unexecuted and contain no sealed answer key; external evaluation remains necessary.
