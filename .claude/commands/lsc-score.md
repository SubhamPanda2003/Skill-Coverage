---
description: Score the real evals collected by /lsc-run-benchmark and show the resulting coverage/conflict metrics. Free, deterministic, safe to re-run.
---

Run `python3 score_evals.py`.

If it fails because an eval run is missing, tell me to run `/lsc-run-benchmark` first -- don't try to invent or fill in missing runs yourself.

This always recomputes every Verifiable-tier `grading.json` entry fresh from each eval's `outputs/response.md` (preserving whatever Judged-tier verdicts `/lsc-run-benchmark`'s judge step already recorded), then writes each skill's own `<skill>-workspace/iteration-N/benchmark.json` plus the whole-suite rollup at `results/iteration-N/benchmark.json`.

Summarize the resulting root `results/iteration-N/benchmark.json` for me in the same style as `docs/results.md`: report `TaskSuiteCoverage`, `RetrievalRate`, `ComplianceCoverage`, and the conflict metrics, and call out anything that looks like a real finding worth investigating (e.g. a constraint that's `Unretrieved` across every task, or a conflict pair with a low `ConflictResolutionRate`). Note explicitly whether `results/iteration-N/benchmark.json` has a `MutationScore` yet -- that field only exists after `/lsc-mutate` has run for this iteration and folded it in via `score_mutation_evals.py`.
