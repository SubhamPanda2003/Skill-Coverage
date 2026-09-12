---
description: Run every LSC benchmark task through a real, isolated lsc-worker subagent to generate genuine trajectories, then judge the Judged-tier constraints with lsc-judge. Costs real subagent calls -- run deliberately, not on a loop.
---

Run the Layered Skill Coverage benchmark end to end using real subagents -- do not hand-author any artifact yourself.

1. Read `benchmark/tasks.json` (a list of `{id, text, expects}`).
2. For every task, invoke the Agent tool with `subagent_type: lsc-worker`, passing exactly that task's `text` as the prompt -- nothing added, no hints about skills or evaluation. Batch independent tasks into parallel Agent calls in one message rather than one at a time. Capture each subagent's final response verbatim as that task's artifact.
3. For each task, use the Write tool to save `results/trajectories/<task_id>.json` containing `{"artifact": "<the subagent's verbatim output>"}`. Create the `results/trajectories/` directory if it doesn't exist.
4. Run `python3 list_judgment_needed.py` and read its output -- one JSON line per `(task_id, key, unit_text)` that needs a judged verdict.
5. For each of those lines, invoke the Agent tool with `subagent_type: lsc-judge`, giving it the `unit_text` and the matching task's artifact (from the trajectory file you just wrote in step 3). Parse the "Verdict: Pass" or "Verdict: Fail" line from its reply.
6. Update each affected `results/trajectories/<task_id>.json` to add a `"judged_verdicts"` object mapping `key -> "Pass"|"Fail"` (merge into the existing file, don't overwrite the artifact).
7. Report back to me: how many worker subagents ran, how many judge calls ran, and flag by task id any worker output that looked degenerate -- empty, a refusal, or something that clearly didn't attempt the task -- rather than silently letting it get scored as a Fail.
8. Do not run `score_trajectories.py` yourself. That's `/lsc-score`, kept separate so I can re-score without re-paying for subagent calls.
