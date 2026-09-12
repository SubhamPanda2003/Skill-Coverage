---
description: Score the real trajectories collected by /lsc-run-benchmark and show the resulting coverage/conflict metrics. Free, deterministic, safe to re-run.
---

Run `python3 score_trajectories.py`.

If it fails because trajectory files are missing, tell me to run `/lsc-run-benchmark` first -- don't try to invent or fill in missing trajectories yourself.

Otherwise, summarize the resulting `results/live/results.json` for me in the same style as `docs/results.md`: report `TaskSuiteCoverage`, `RetrievalRate`, `ComplianceCoverage`, and the conflict metrics, and call out anything that looks like a real finding worth investigating (e.g. a constraint that's `Unretrieved` across every task, or a conflict pair with a low `ConflictResolutionRate`). Note explicitly that this run has no mutation-adequacy score yet (that needs a second subagent round against mutated skills, not yet built).
