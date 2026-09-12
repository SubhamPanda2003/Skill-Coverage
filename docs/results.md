# Pilot Results: Layered Skill Coverage

*Run 2026-09-12. Code: [`lsc/`](../lsc/), benchmark skills: [`.claude/skills/`](../.claude/skills/) (moved here after this pilot ran, so real Claude Code sessions can also discover them — see the `/lsc-run-benchmark` command), orchestration: [`run_pilot.py`](../run_pilot.py), raw output: [`results/results.json`](../results/results.json), visual report: [`results/report.html`](../results/report.html).*

*This pilot's Scope section (below) opens with "no live LLM agent was available to script in this environment." That gap has since been closed — see [Part 2: Live Subagent Run](#part-2-live-subagent-run-2026-09-12) at the end of this document for real `lsc-worker`/`lsc-judge` trajectories against the same pipeline.*

## Scope — read this before the numbers

**No live LLM agent was available to script in this environment** (no API key configured for the Anthropic API, and no access to spin up Codex/OpenHands/other agent harnesses at SkillsBench scale). The trajectories used below are **hand-constructed by the pipeline author** to exercise every path the pipeline needs to distinguish — pass, fail, unretrieved, conflicting skills, mutation-killed, mutation-survived — with known ground truth. This is the same methodology you'd use to unit-test a coverage tool before trusting it on real, expensive, uncontrolled agent runs. **These are not live multi-model results and the numbers below say nothing about how any real agent actually behaves.** What they validate is that the *pipeline itself* computes the intended metrics correctly against known inputs.

## Benchmark

Four skills, each a valid `SKILL.md` per the agentskills.io spec (`name` + `description` frontmatter, progressive-disclosure-compatible):

| Skill | Purpose in the pilot |
|---|---|
| `text-styling` | The running compound-conditional example (blue/red font-size branches) — tests verbatim segmentation, branch-pointer anchoring, and the exposure funnel. |
| `indent-tabs` / `indent-spaces` | A deliberately conflicting pair (tabs vs. spaces) loaded together by the same task — tests the new cross-skill conflict-coverage feature. `indent-tabs` also carries a second, easy-to-satisfy-by-default instruction ("end with a trailing newline") to demonstrate mutation-adequacy's diagnostic value. |
| `commit-messages` | One `Judged` unit (imperative mood — no deterministic oracle) alongside one `Verifiable` unit (≤50 characters) in the same skill — tests the type-classification split. |

7 tasks, each annotated with an explicit ground-truth `expects` list (which constraints the benchmark author intends the task to instantiate) — this is the "task-suite design fact" the methodology's `Instantiated` is defined against, kept deliberately separate from the deterministic lexical `discover()` function that decides retrieval, so the two funnel stages are measured independently rather than by the same heuristic.

## Results

| Metric | Value |
|---|---|
| TaskSuiteCoverage | 100% (7/7 constraint-branches instantiated by at least one task) |
| RetrievalRate | 100% (aggregate — see the masking finding below) |
| ComplianceCoverage | 85.7% (6/7) |
| VerifiableCoverage | 83.3% (5/6) |
| JudgedCoverage | 100% (1/1) |
| ConflictPairsDetected | 1 (the tabs/spaces pair — correctly found, no false positives against the unrelated "trailing newline" or `commit-messages`/`text-styling` units) |
| ConflictResolutionRate | 50% (1 of 2 instances where both skills were loaded together, the agent produced internally consistent output) |
| MutationScore | 50% (1 of 2 mutation trials) |

## What the pipeline correctly caught

**The branch-pointer design holds up under real code.** The `text-styling` sentence — *"If the color of the text is blue then change the font to 20px and if color is red then change it to 30 px"* — is rendered in the report **whole and verbatim**, exactly as written, with the blue and red clauses independently highlighted as separate branch pointers. The pronoun "it" in the red clause is never separated from its antecedent. This was the specific failure mode the methodology was designed to avoid (see [proposed-methodology.md](proposed-methodology.md) §4), and the implementation preserves it correctly.

**Conflict detection worked with zero false positives on this corpus.** The heuristic (topical keyword overlap + disjoint concrete values across skills) found exactly the one deliberately-planted conflicting pair, out of 6 candidate Verifiable units, without flagging the unrelated "trailing newline" instruction. `ConflictResolutionRate` (50%) is a genuinely different number from either skill's raw `ComplianceCoverage` — `indent-spaces` shows a flat **Fail** (0%) because a spaces-vs-tabs conflict structurally guarantees one side loses, but that's the wrong question; `ConflictResolutionRate` asks whether the agent's choice was at least *internally consistent* (all-tabs or all-spaces) rather than mixed within one file, and correctly distinguishes the `t_code_consistent` trajectory (Pass) from `t_code_mixed` (Fail) — the exact diagnostic distinction a plain compliance metric can't make.

**Mutation-adequacy separated a load-bearing instruction from a decorative one, using the same compliance-coverage number.** Both `text-styling`'s red-branch instruction and `indent-tabs`'s trailing-newline instruction show **100% compliance coverage** in isolation — every task that exercised them passed. Mutation testing tells a different story: deleting the red/30px instruction and rerunning `t_red` flips the verdict from Pass to Fail (**killed**) — the eval suite would notice this instruction disappearing. Deleting the trailing-newline instruction and rerunning `t_code_consistent` changes nothing — the mutant artifact is identical to the original (**not killed**) — because ending a file with a newline is default tool/editor behavior the agent does regardless of the instruction. Same compliance score, opposite adequacy verdict. This is the concrete demonstration the methodology's §3 Stage 8 argued for in the abstract; here it's a reproducible result from running code.

## An honest finding: the aggregate rollup hides exactly the thing it's supposed to surface

`RetrievalRate` reports **100%** — but `t_red_unretrieved` was deliberately built so the loader's lexical discovery check would **fail** to activate `text-styling` even though the task's `expects` annotation says the red-branch condition was intended to be instantiated. Looking only at the headline metric, you would never know this happened: the per-key rollup takes the best outcome across every task that touches a given constraint ("Pass if any task ever passed"), and `t_red` — a different, successful task — retrieves and passes the same branch, masking `t_red_unretrieved`'s failure in the aggregate.

The **per-task table** (in `report.html` and `results.json`'s `per_task` field) does show it correctly: `t_red_unretrieved → text-styling#u0#b1 → Unretrieved`. This is a real methodological lesson, not a bug fixed after the fact — the same "collapsed number hides the diagnosis" critique the methodology levels at Skill Coverage's single covered/Pass/Fail signal (§0, §3 Stage 6) turned out to apply to *this* pipeline's own naive rollup the first time it was actually run. The fix implemented here — always report per-task detail alongside the aggregate, never the aggregate alone — should be treated as a required part of the design, not an optional reporting nicety. Updated in the methodology doc.

## Limitations of this pilot specifically

- **N=1 "agent"** (the pipeline author, constructing labeled trajectories by hand) — no claim about real model behavior.
- **Conflict detector validated on one designed case.** It has not been run against a corpus of real, independently-authored skills where conflicts arise organically rather than being planted.
- **Discovery/segmentation regexes are simple** (word-overlap lexical matching, sentence-boundary + conjunction/pronoun guards) and were only exercised against four short, clean skills written for this pilot — not yet stress-tested against messy real-world `SKILL.md` files at SkillsBench scale.
- **`Judged`-tier verdicts were supplied directly** (`judged_verdicts` in the trajectory fixtures) rather than produced by an actual LLM judge. No API call was ever planned for this — `oracle.evaluate` only ever does a dictionary lookup; the real judge call was always meant to happen one layer up, as a Claude Code subagent invoked by the orchestrating command. That layer just didn't exist yet when this pilot ran (see Part 2, where it does).

## Next steps

1. ~~Wire `oracle.evaluate`'s `Judged` path to a real LLM judge call~~ — **done in Part 2, below**, but not the way this item implies: `oracle.evaluate` itself is unchanged and still just looks up a pre-computed verdict. The real judge call happens one layer up, as a `lsc-judge` Claude Code subagent that `/lsc-run-benchmark` invokes per Judged-tier unit; its verdict is what now gets handed to `oracle.evaluate` instead of a hand-supplied fixture. Validating those verdicts against a small human-labeled sample (the κ-agreement check) is still outstanding — see Part 2's Next Steps.
2. Run discovery/segmentation against a sample of real SkillsBench skills to see how often the anaphora-guard and conflict-detector heuristics hold up outside of hand-written examples.
3. ~~If API access becomes available, replace the hand-authored trajectories with real agent runs~~ — **done in Part 2, below**, and not via API access: no Anthropic API key was ever used or needed. The replacement trajectories came from Claude Code subagents (`lsc-worker`) spawned by the `/lsc-run-benchmark` command inside a live session. See Part 2 for whether the qualitative findings above (branch-pointer fidelity, conflict-resolution consistency, mutation sensitivity) survived contact with real model outputs.

---

## Part 2: Live Subagent Run (2026-09-12)

*Same day as the pilot above, run after it. Code: [`lsc/`](../lsc/) (with two bugs fixed mid-run — see below), benchmark: grown to six skills / twelve tasks (`error-handling` and `docstring-style` added since the pilot), orchestration: the `/lsc-run-benchmark`, `/lsc-score`, and `/lsc-mutate` commands driving real `lsc-worker`/`lsc-judge` Claude subagents, raw output: [`results/live/results.json`](../results/live/results.json), mutation output: [`results/mutation/results.json`](../results/mutation/results.json).*

### Scope

This is the first run using **real, uncontrolled Claude subagent output** end to end — closing the exact gap the pilot above flagged as its central limitation ("no live LLM agent was available to script in this environment"). Twelve tasks were each sent to a fresh, isolated `lsc-worker` subagent with nothing but the task text (no mention of skills or evaluation); Judged-tier units were scored by real `lsc-judge` subagent calls instead of pre-supplied verdicts; mutation-adequacy applied real single-unit deletions to the live `.claude/skills/*/SKILL.md` files and reran the affected task through a fresh subagent each time.

This is still **N=1: one run, one model, no repeated trials.** Treat it as a second data point that validates the pipeline against real model output, not as a general claim about how any model follows skills.

### Results

| Metric | Value |
|---|---|
| TaskSuiteCoverage | 100% (17/17 constraint-branches instantiated) |
| RetrievalRate | 100% (aggregate — see masking finding below) |
| ComplianceCoverage | 64.7% (11/17) |
| VerifiableCoverage | 54.5% (6/11) |
| JudgedCoverage | 83.3% (5/6) |
| ConflictPairsDetected | 3 |
| ConflictInstantiatedRate | 33.3% (1 of 3 detected pairs actually co-occurred in a task) |
| ConflictResolutionRate | 100% (2/2 co-occurring instances internally consistent) |
| MutationTrials | 12 |
| MutationScore | 8.3% (1/12 killed) |

### Two real bugs this run exposed, and fixed

Neither of these is specific to synthetic vs. live data — both would have silently corrupted any run. They only surfaced now because this was the first run against a corpus varied enough to trip them; the pilot's small hand-picked fixtures never exercised these code paths.

1. **Oracle false-negative** (`lsc/oracle.py`). The `docstring-style` "wrap at 79 characters" check scanned the *entire* raw artifact string instead of just the docstring text, so an otherwise-compliant docstring could fail because of a stray sentence the agent wrote outside the code fence. Fixed by scoping the check to text inside triple-quoted strings only. This alone moved `ComplianceCoverage` from 58.8% to 64.7%.
2. **Mutation-score contamination** (`score_mutations.py`). It scored every file in `results/mutants/` rather than scoping to the current run's actual candidates, so three leftover files from this same pilot's earlier hand-authored fixtures silently inflated the trial count (7.1% reported vs. 8.3% actual). Fixed by deriving the candidate set directly from `results/live/results.json` (identical logic to `list_mutation_candidates.py`) and explicitly skipping and naming anything else found on disk.

### What held up

- The exposure funnel, conflict detector, and per-task/per-key rollup all worked against real, uncontrolled model output exactly as they did against the hand-authored fixtures — the pipeline's design generalizes past the fixtures it was built against.
- `ConflictResolutionRate` again did its job on the one conflict pair actually instantiated together (`indent-tabs` vs. `indent-spaces`): both `t_code_consistent` and `t_code_mixed` came back internally consistent (all-spaces), never mixed within a file.
- The pilot's retrieval-masking finding reproduced exactly as predicted: `RetrievalRate` reports 100% in aggregate, but `t_red_unretrieved` shows `Unretrieved` in `per_task` the whole time — the aggregate rollup still hides it, confirming that finding wasn't an artifact of hand-authored data.

### Honest findings

**Three worker trajectories are degenerate, not genuinely non-compliant.** `t_blue`, `t_red`, and `t_red_unretrieved` (all `text-styling` tasks) show the same broken pattern: the subagent described a bash tool call in its final response text but never actually invoked it (`tool_uses: 0`), and never touched a heading element. `text-styling`'s resulting 0% compliance in this run is an artifact of that failure mode, not evidence the skill was disregarded.

**`commit-messages` also shows 0% compliance, for a different and legitimate reason.** Both commit-message tasks ran in an isolated environment with no git repo or diff to summarize; the worker correctly asked for context rather than fabricating a commit message. Reasonable agent behavior, zero artifact produced, so it fails by construction — a task/environment mismatch, not a skill failure.

**Mutation-adequacy's low score survived a direct test of the "leading task text" hypothesis — which means the explanation is different from what it looked like.** The original hypothesis: 11 of 12 live trials came back `killed: false` because the task prompts restated the exact requirement in plain English. That hypothesis made a testable prediction — rewrite the prompts to state only the goal, and the score should rise. It didn't. See the follow-up experiment below.

### Limitations of this run specifically

- N=1 run, one model, no repeated trials — same caveat the pilot gave for its synthetic data, now attached to real output instead.
- No human-labeled κ-agreement check has been run against the `lsc-judge` verdicts yet — see Part 3 below for the check itself, once labels come back.

### Next steps

1. ~~Rewrite the `error-handling`/`docstring-style` task prompts~~ and ~~rerun `t_blue`/`t_red`/`t_red_unretrieved`~~ — **done, same day, see Part 3.**
2. Run the κ-agreement check — **in progress, see Part 3.**
3. Given Part 3's finding that `error-handling`/`docstring-style` instructions align with the model's pretrained defaults rather than needing the skill at all: find or write task/skill pairs where the skill instruction cuts *against* a plausible default (like `indent-spaces` does), to get a mutation-adequacy signal that isn't structurally pre-determined by what the base model already tends to do.

---

## Part 3: Follow-up Experiments, Same Day

*Three of Part 2's own Next Steps, run the same day as a direct test of Part 2's hypotheses rather than left as future work. Trajectories: same `results/trajectories/` and `results/mutants/` (files overwritten in place for the 9 affected tasks/candidates), rescored via the same `/lsc-score` and `/lsc-mutate` pipeline.*

### De-leading the task prompts didn't move the mutation score — a real, useful negative result

Part 2 hypothesized that 11 of 12 mutation trials came back `killed: false` because the task prompts restated the skill's exact mechanism ("raise ... with the original exception chained using `from`", "documenting its parameter, return value, and the exception it can raise"). That's a falsifiable claim: rewrite the prompts to state only the goal, rerun, and the score should rise if the hypothesis is right.

`t_errhandle_good`, `t_docstring_good`, and `t_combo_err_doc` were rewritten to name only the goal (e.g., "handling the case where a file is missing and the case where a file's content isn't valid JSON" instead of spelling out log-and-skip / raise-and-chain), verified to still retrieve the right skills via `lsc/core.py`'s `discover()`, then rerun through fresh `lsc-worker` subagents and rejudged. Compliance was unaffected — `ComplianceCoverage` held at 64.7% — and every mutation trial on the de-leaded prompts still came back `killed: false`. **`MutationScore` is unchanged: 8.3% (1/12).**

That's the hypothesis failing its own test, and the failure is informative: if the task text were doing the work, removing it should have exposed at least some decorative instructions as genuinely unenforced. It didn't move at all. The likelier explanation: `error-handling`'s bare-except ban, its exception-chaining rule, and `docstring-style`'s Google-style Args/Returns/Raises convention are all things this model already does by default from pretraining, task text or skill or not — chaining with `from` and writing Google-style docstrings are extremely common patterns in Python code the model has seen, not niche conventions this skill introduces. `indent-spaces#u0#b0` is the one instruction that *was* killed, and it's the one case where the alternative (tabs) is roughly as plausible a default as the instructed behavior (spaces) — the skill has something to add specifically because the model has no strong prior either way. **The real predictor of mutation-adequacy here looks like "does this instruction fight a default the model already has," not "is this instruction restated in the task text."** That reframes Next Steps item 3 above: future mutation-testing tasks should target instructions that plausibly cut against a pretrained default, not just avoid restating the mechanism in the prompt.

### The degenerate `text-styling` pattern is real but not deterministic

Rerunning `t_blue`, `t_red`, and `t_red_unretrieved` with identical prompts: `t_blue` and `t_red` reproduced the exact same failure (a described-but-never-executed tool call, `tool_uses: 0`) on the second attempt. `t_red_unretrieved` did not — it produced a fully compliant artifact (`color: red; font-size: 30px`) this time. Recurring at roughly 2-in-3 across two independent samples per task is enough to call this a real, non-negligible failure mode of this task shape (an empty working directory with no actual heading element to find) rather than a one-off fluke, but it's not deterministic either — same prompt, different outcome, on the same task twice.

This also sharpens the pilot's original retrieval-masking finding. `t_red_unretrieved`'s task text ("Ship the heading in red now.") still doesn't lexically overlap `text-styling`'s keywords, so `lsc/core.py`'s `discover()` heuristic still marks it `Unretrieved` in `per_task` — but the real subagent produced fully compliant output anyway. The deterministic lexical retrieval check and the real subagent's actual behavior now visibly disagree on this exact task, in both directions across the two pilots: the methodology's own retrieval predictor is a heuristic proxy, not a ground truth reading of what the live model actually did.

### κ-agreement check: pending

A 10-item human-labeling sample was prepared from every `Judged`-tier verdict produced by real `lsc-judge` calls so far (5 tasks, 10 (task, key) pairs) — see the request accompanying this update. Agreement will be computed and reported here once labels come back.

### Housekeeping

All of this session's work — the pipeline, the pilot, the live run, both bug fixes, and this follow-up — is now committed to git (previously everything past the initial `LICENSE`/`README.md` commit was untracked). `text_analyzer.py`'s relevance to this project is still unresolved but no longer at risk of being lost either way.
