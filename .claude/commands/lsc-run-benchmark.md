---
description: Run every LSC eval through a real, isolated lsc-worker subagent to generate genuine trajectories, then judge the Judged-tier constraints with lsc-judge. Costs real subagent calls -- run deliberately, not on a loop.
---

Run the Layered Skill Coverage benchmark end to end using real subagents -- do not hand-author any artifact yourself.

1. Read every eval from `.claude/skills/*/evals/evals.json` (per-skill) and `evals/cross-skill.json` (evals that deliberately target 2+ skills at once) -- each entry is `{id, prompt, expected_output, assertions, lsc_targets}`. `expected_output` is spec-required shape but LSC never reads it; `lsc_targets` is LSC's actual ground truth, a list of `[skill, unit_index, branch_index]` triples.
2. For each eval, determine its workspace: `.claude/skills/<skill>-workspace/` if it targets exactly one skill, `cross-skill-workspace/` (repo root) if it targets more than one. Determine the run's iteration number: one more than the highest existing `iteration-N` under that workspace (0 if none exist yet) -- a fresh `/lsc-run-benchmark` call always starts a new iteration, it never overwrites a previous one.
3. For every eval, invoke the Agent tool with `subagent_type: lsc-worker`, passing exactly that eval's `prompt` as the prompt -- nothing added, no hints about skills or evaluation. Batch independent evals into parallel Agent calls in one message rather than one at a time. Capture each subagent's final response verbatim as that eval's artifact, and note the `total_tokens`/`duration_ms` from its completion notification's usage block.
4. For each eval, write to `<workspace>/iteration-N/eval-<id>/with_skill/`:
   - `outputs/response.md` -- the verbatim artifact text.
   - `timing.json` -- `{"total_tokens": <int>, "duration_ms": <int>}` from step 3's usage block.
   Do not write `grading.json` yet for Verifiable-tier assertions -- that's `/lsc-score`'s job, always recomputed fresh from `outputs/response.md` so an oracle fix propagates without rerunning subagents. Judged-tier assertions do need a subagent (steps 5-6 below) and their verdict must be captured now, since a plain script can't produce one later.
5. Run `python3 list_judgment_needed.py` and read its output -- one JSON line per `(task_id, key, unit_text)` that needs a judged verdict.
6. For each of those lines, invoke the Agent tool with `subagent_type: lsc-judge`, giving it the `unit_text` and the matching eval's artifact (from the `outputs/response.md` you just wrote). Parse the "Verdict: Pass" or "Verdict: Fail" line and the reasoning from its reply.
7. For each Judged-tier verdict from step 6, write (or merge into) `<eval_dir>/with_skill/grading.json`'s `assertion_results` list: `{"text": <verbatim unit text>, "lsc_key": "<skill>#u<N>#b<N>", "passed": <bool from the verdict>, "evidence": <the judge's cited reasoning, verbatim>}`. Leave Verifiable-tier keys out of this file for now -- `/lsc-score` fills those in.
8. Report back to me: how many worker subagents ran, how many judge calls ran, and flag by eval id any worker output that looked degenerate -- empty, a refusal, or something that clearly didn't attempt the task -- rather than silently letting it get scored as a Fail.
9. Do not run `score_evals.py` or `score_mutation_evals.py` yourself. That's `/lsc-score`, kept separate so I can re-score without re-paying for subagent calls.
