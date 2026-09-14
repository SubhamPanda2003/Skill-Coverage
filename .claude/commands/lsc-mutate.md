---
description: Live mutation-adequacy testing -- for every constraint that scored Pass in the /lsc-score run, delete it from the real skill file, rerun that eval through a fresh subagent, and check whether the outcome flips. Requires /lsc-run-benchmark and /lsc-score to have already run. Costs one subagent call per candidate.
---

Run live mutation-adequacy testing. Requires `results/iteration-N/benchmark.json` to already exist (from `/lsc-run-benchmark` then `/lsc-score`) -- if it doesn't, tell me to run those first and stop.

1. Run `python3 list_mutation_candidates.py` and read its output -- one JSON line per `(task_id, key, skill, unit_index, task_text)` candidate.
2. For each candidate, in sequence (not parallel -- these mutate a shared file, so two at once on the same skill would corrupt each other):
   a. Run `python3 mutate_skill.py apply <skill> <unit_index>`.
   b. Invoke the Agent tool with `subagent_type: lsc-worker`, passing exactly that candidate's `task_text` as the prompt -- same as the original run, nothing added.
   c. **Immediately**, regardless of whether step (b) succeeded, errored, or produced something strange: run `python3 mutate_skill.py restore <skill>`. Never move to the next candidate, and never end this command, while a skill file is left in its mutated state.
   d. Determine that candidate's eval directory the same way `/lsc-run-benchmark` does: `<workspace>/iteration-N/eval-<task_id>/`, using the *same* iteration number as that eval's `with_skill/` run (a mutation trial is a variant of an existing run, not a new iteration). Write the subagent's verbatim output to `<eval_dir>/mutant_<key>/outputs/response.md`, where `<key>` is already in the safe `skill#uN#bN` form (e.g. `mutant_docstring-style#u2#b0/`). No `timing.json`/`grading.json` needed here -- `/lsc-score` fills in `grading.json` fresh from `outputs/response.md`.
3. After all candidates are processed and every skill file is confirmed restored to its original content, run `python3 score_evals.py` (to refresh every `grading.json`, including the new mutant ones, from the current on-disk artifacts) and then `python3 score_mutation_evals.py` (which folds `MutationScore`/`MutationTrials` into `results/iteration-N/benchmark.json` -- run these two in that order, since the mutation scorer reads the root file the first script just wrote).
4. Report the `MutationScore` to me, and specifically call out any candidate where `killed: false` -- that's a constraint the eval suite currently can't tell you if you delete, which is worth knowing about independent of its compliance score.

If anything goes wrong mid-loop, prioritize restoring the skill file over continuing -- run `python3 mutate_skill.py restore <skill>` for whichever skill you were last mutating before reporting the error to me.
