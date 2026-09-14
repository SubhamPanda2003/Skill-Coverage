# Pilot Results: Layered Skill Coverage

*Run 2026-09-12. Code: [`lsc/`](../lsc/), benchmark skills: [`.claude/skills/`](../.claude/skills/) (moved here after this pilot ran, so real Claude Code sessions can also discover them — see the `/lsc-run-benchmark` command).*

*This pilot's Scope section (below) opens with "no live LLM agent was available to script in this environment." That gap has since been closed — see [Part 2: Live Subagent Run](#part-2-live-subagent-run-2026-09-12) at the end of this document for real `lsc-worker`/`lsc-judge` trajectories against the same pipeline.*

*Migration note: the file layout described in this document (`benchmark/tasks.json`, `run_pilot.py`, `score_trajectories.py`, `score_mutations.py`, `results/trajectories/`, `results/mutants/`, `results/live/`, `results/mutation/`, `results/results.json`, `results/report.html`) was frozen after Part 3 below, then later removed entirely from the working tree to keep the repo to a single current benchmark rather than carrying old and new layouts side by side. Every number quoted in Parts 1–3 is still exact and still reproducible — the underlying files are just a `git log`/checkout away in the pre-migration commits, not present in the working tree. Current runs use `.claude/skills/<skill>/evals/evals.json` + `evals/cross-skill.json` for eval definitions, `<skill>-workspace/`/`cross-skill-workspace/iteration-N/` for run artifacts, and `score_evals.py`/`score_mutation_evals.py` for scoring, aligning with the real [agentskills.io evaluation convention](https://agentskills.io/skill-creation/evaluating-skills) instead of a bespoke LSC-only layout. See [Part 4](#part-4-folding-lsc-into-the-agentskillsio-convention) for why and how.*

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

All of this session's work — the pipeline, the pilot, the live run, both bug fixes, and this follow-up — is now committed to git (previously everything past the initial `LICENSE`/`README.md` commit was untracked). `text_analyzer.py` — unrelated to this project, unreferenced anywhere, not part of the original commit — was later confirmed stale and removed.

---

## Part 4: Folding LSC into the agentskills.io Convention

*Same live-run data as Parts 2–3, reshaped into a new file layout — no new subagent calls, no methodology change. Verified: every funnel/conflict/mutation number below is byte-identical to Parts 2–3's, recomputed via the same unmodified `lsc/analysis.py` functions from the same underlying artifacts.*

### Why

Everything above lives in a layout nothing else in the ecosystem uses. agentskills.io — the real spec this project's `SKILL.md` files already conform to — separately publishes an [evaluation convention](https://agentskills.io/skill-creation/evaluating-skills): each skill owns `evals/evals.json`, runs land in `<skill>-workspace/iteration-N/eval-<id>/{with_skill,without_skill}/{outputs/,timing.json,grading.json}`, aggregated into a `benchmark.json`. It answers a different question than LSC does (does the skill help at all, via with/without-skill A/B, vs. LSC's which-specific-instruction-got-followed), but the shapes overlap enough to fold LSC in almost entirely additively.

### What changed

- `benchmark/tasks.json` → per-skill `.claude/skills/<skill>/evals/evals.json`, plus `evals/cross-skill.json` for the 3 evals that deliberately target 2+ skills at once (`t_code_consistent`, `t_code_mixed`, `t_combo_err_doc` — conflict-testing is inherently cross-skill; the base spec has no concept of this, so the file says so explicitly). Field names: `text`→`prompt`, `expects`→`lsc_targets` (an additive, ignorable-by-others field carrying LSC's actual ground truth), plus a new `expected_output` one-liner per eval that the base spec wants but **LSC never reads** — written for shape-completeness only.
- `results/trajectories/`/`results/mutants/` (flat files) → `<skill>-workspace/`/`cross-skill-workspace/iteration-1/eval-<id>/{with_skill,mutant_<key>}/{outputs/response.md, timing.json, grading.json}`. `grading.json` (`{assertion_results:[{text,passed,evidence}], summary}`) gets one additive field per assertion, `lsc_key`, mapping back to the `(skill,unit,branch)` tuple `oracle.evaluate` is keyed on.
- Each skill now gets its **own real, non-stub `benchmark.json`** — `lsc/analysis.py::run_funnel` already accepted a `skills` subset as a parameter, so calling it with one skill produces a fully valid scoped `TaskSuiteCoverage`/`ComplianceCoverage` for that skill alone. `indent-tabs` and `indent-spaces` have no single-skill eval of their own (every task touching them is cross-skill, by design), but their workspace `benchmark.json` still shows real computed numbers, sourced entirely from the cross-skill evals.
- `results/live/results.json`/`results/mutation/results.json` → `results/iteration-1/benchmark.json` (whole-suite rollup: same fields Parts 1–3 already reported, `TaskSuiteCoverage`/`RetrievalRate`/`ComplianceCoverage`/conflict metrics/`MutationScore`, additive on top of the spec's own `run_summary`/`delta` shape).
- `score_trajectories.py`/`score_mutations.py` were **forked**, not edited — `score_evals.py`/`score_mutation_evals.py` are new scripts reading the new layout. (The originals and the flat legacy data they read were later removed from the working tree entirely — see the migration note at the top of this document — but forking rather than editing in place is why Parts 1–3's numbers stayed reproducible from git history right up until that removal.)
- `timing.json` (`{total_tokens, duration_ms}`) is a genuine new capability, not a rename — nothing before this recorded per-run cost, despite `docs/proposed-methodology.md` §7 flagging it as an unaddressed threat to validity. It's marked `null` with an honest note for this backfilled iteration-1, since presenting imprecisely-recalled historical numbers as recorded fact would be worse than not having them; real capture starts with the next live run under the updated `/lsc-run-benchmark`.

### Two things this migration found, beyond the file move itself

**A real, pre-existing bug in `run_funnel`, only exposed now that it's called with a skill subset.** `instantiated[key] = True` was writing unconditionally, even for keys whose skill wasn't in the `skills` argument at all — every prior call always passed all 6 skills, so this never mattered until per-skill scoring needed a real subset. It silently inflated `TaskSuiteCoverage` past 100% (a scoped call returned `3.4` instead of a fraction) and polluted `per_task` with bogus cross-skill entries. Fixed with a one-line guard (`if key not in instantiated: continue`); reverified the full 6-skill path is completely unaffected before trusting the fix.

**`sync_workspace_root.sh` would have swept every eval-run artifact into the workspace-root mirror.** `<skill>-workspace/` sits inside `.claude/skills/` (matching the spec's sibling-directory convention), and the existing sync script's `cp -r .claude/skills/*` doesn't distinguish a skill directory from a workspace directory — it would have copied every `outputs/response.md` and `grading.json` on every sync, for no reason (the mirror exists to make skills discoverable to a live session, not to replicate eval history). Fixed by skipping `*-workspace` entries in the copy loop, plus a defensive prune for anything an older script version already leaked in.

### Verification

`results/iteration-1/benchmark.json`'s funnel numbers (`ComplianceCoverage` 64.7%, etc.) and `MutationScore` (8.3%, 1/12) are confirmed byte-identical to the frozen `results/live/results.json`/`results/mutation/results.json` they were reshaped from — this is a pure layout change, carrying zero new empirical claims. The next live run under this layout is the first real test of whether the convention holds up under fresh subagent calls rather than a backfill of already-final data.

---

## Part 5: The 25-Skill Expansion

*19 new skills added to the same tree Part 4 built, each designed against one question: does this instruction plausibly fight a pretrained model default, align with one, or is it unclear? This was Part 4's own conclusion's flagged next step, run for real — across two live attempts, one day apart, the first of which turned out to be invalid. This section reports the corrected picture directly rather than the invalid first attempt; see "A bug invalidated the first attempt," below, for what that attempt got wrong and why it isn't reported as a data point.*

### Design

19 skills, single-instruction each, split 10 predicted-fight / 6 predicted-align / 3 predicted-uncertain (`quote-style`, `trailing-comma`, `error-period`) — deliberately skewed toward fight, since those are the candidates likeliest to actually get killed under mutation testing, which is what makes this set more informative than the original 12-task benchmark's 1-of-12 killed rate. Examples: `variable-naming` (camelCase, fights PEP8), `mutable-default-ban` (no mutable default args, aligns with a heavily-trained-in gotcha), `em-dash-ban` (no em dashes in prose, fights an observed Claude stylistic tic). Every skill was verified before spending on subagents: each segments as a single clean unit, each task prompt actually retrieves its skill via `core.discover()`, and every deterministic checker was tested against a hand-built pass/fail pair before use (all 18 passed).

### A bug invalidated the first attempt

The `lsc-worker` subagent relies entirely on a `skills:` frontmatter preload list to see any skill content at all (it runs with no tools, so it can't look one up at runtime either). That list was written for the original 6-skill pilot and never updated for this expansion — so for the first attempt at this run, **19 of these 25 skills were never actually visible to the worker**, even though the pipeline reported 100% retrieval (a topic-keyword proxy, not evidence of real access). The model was generating unguided default output on those 19 skills' tasks, not skill-influenced output. That run's numbers (`ComplianceCoverage` 52.8%, `MutationScore` 5% (1/20)) aren't a finding about the model — they're an artifact of the bug — so they're recorded here only as history, not reported as data.

Fixed by adding all 25 skill names to the preload list, then run twice more, one day apart, giving two independent, properly-configured samples of the same 19-skill set. (The mutation scorer also had a separate bug of its own, found on the second of these two runs — see below.)

### Results: two valid samples, and a swing bigger than the invalid run ever suggested

| Metric | Sample 1 (2026-09-13, corrected) | Sample 2 (2026-09-14) |
|---|---|---|
| TaskSuiteCoverage | 100% | 100% |
| RetrievalRate | 100% | 100% |
| **ComplianceCoverage (this 19-skill set, 21 keys)** | **33.3% (7/21)** | **76.2% (16/21)** |
| ConflictPairsDetected | 7 | 7 |
| ConflictInstantiatedRate | 14.3% | 14.3% |
| ConflictResolutionRate | 100% (2/2) | 100% (2/2) |
| MutationScore (whole 25-skill suite) | not computed — contaminated by the preload bug | 9.7% (3/31), first clean measurement |

**All 6 predicted-align skills passed compliance in both samples, with zero exceptions.** That part replicated perfectly. **The 10 predicted-fight skills did not replicate at all**: all 10 failed in Sample 1 — a sharper failure mode than Part 3's finding, since Part 3 showed the model doing what it would do anyway while this looked like the model being told directly to do something (camelCase names, `+` concatenation instead of f-strings, no `is_`/`has_`/`should_` prefixes, 60-character lines) and doing the opposite. But in Sample 2, only 3 (`date-format`, `currency-format`, `test-naming`) failed cleanly, 1 (`variable-naming`) split across its two branches, and the other 6 passed outright. **"Fight-predicted instructions get actively overridden" was true of Sample 1 and false of Sample 2 — it doesn't hold up as a stable finding.** What does hold up: alignment with a pretrained default predicts compliance robustly (6/6, twice); fighting one predicts instability, not a reliable override.

**Mutation-adequacy's blind spot is real, but how much it distorts the score depends on which sample you happened to draw.** `list_mutation_candidates.py` only considers units that already scored Pass — a Fail can't be "killed" further. In Sample 1, all 10 failed fight-predicted skills were excluded before mutation testing ever ran, leaving the eligible pool dominated by align-predicted instructions — exactly the ones least likely to be killed, and the mechanical reason that (contaminated) run's `MutationScore` read so low. In Sample 2, 6 more fight-predicted instructions passed and became mutation-eligible for the first time; the corrected, uncontaminated `MutationScore` across the full 25-skill suite came out to 9.7% (3/31) — still low, but two of the three kills (`fstring-required`, `string-concat`, below) now come from that newly-eligible fight-predicted pool. **This is a real limitation in the current definition of mutation-adequacy**, not a limitation of this benchmark: scoping mutation trials to `Pass`-verdict units makes the metric structurally blind to whichever instructions failed on a given draw — and which instructions that is changes sample to sample. Fixing this would mean either mutation-testing `Fail`-verdict units too (checking whether the failure gets *worse*, or whether some other property changes) or reporting compliance-failure and mutation-adequacy as two axes of the same finding rather than a gate between them.

**`em-dash-ban` is the one result that held up identically in both samples, and against mutation testing.** It passed compliance — the model avoided em dashes with the skill loaded — in both samples, which looks like confirmation an explicit instruction can override a stylistic default. But its mutation trial (skill instruction deleted, same task rerun) *also* passed, both times: the model didn't reach for em dashes in this genre of explanatory prose regardless of the skill. Without the mutation check, this would have been misreported as a fight-instruction win twice over.

### A third real bug, found comparing the two samples

`score_mutation_evals.py` computed one global `iteration = max(latest_iteration(ws) for ws in all workspaces)` and applied that single number to every task's eval-directory lookup. Because five of the twenty-five skills' workspaces (`commit-messages`, `docstring-style`, `error-handling`, `text-styling`) plus the cross-skill workspace hadn't yet reached the same iteration number as the rest when Sample 2 was collected, the script looked for `mutant_*` folders under an iteration directory that didn't exist for those tasks and silently found nothing — no error, just missing trials. It reported `MutationTrials: 15` when 31 mutation trials had actually been run and captured; the true `MutationScore` was 9.7% (3/31), not the 20% (3/15) the buggy script returned. Fixed by resolving each task's own workspace iteration independently instead of assuming one global number applies everywhere — mirroring exactly how `score_evals.py`'s `load_evals_trajectories` (via `bench_io.workspace_for_task` + `bench_io.latest_iteration`) already did it correctly (§3.3 of the paper). Reran after the fix; the three real kills didn't change, only the denominator did.

### The three kills, for the first time cleanly

`fstring-required#u0#b0` and both `string-concat` branches (`#u0#b0`, `#u1#b0`) were killed in Sample 2 — the first clean, uncontaminated mutation-adequacy signal either skill has ever gotten, since their Sample-1 trials were contaminated by the preload bug. With the instruction removed in each case, the *other* skill's directly conflicting rule filled the gap: deleting `fstring-required`'s rule made the model fall back to `string-concat`'s `+`-operator convention (still loaded), and deleting `string-concat`'s vowel-substitution rule made the model revert to normal f-strings. Both kills demonstrate a conflicting skill filling a vacuum, not the model reverting to an unprompted pretrained default — worth distinguishing from the "aligns with pretrained default" story the rest of this document tells, since the mechanism here is cross-skill interference, not model prior.

### A finding that contradicts the original pilot

`indent-spaces#u0#b0` was **not** killed in either of its two instantiations in Sample 2 (`t_code_consistent`, `t_code_mixed`) — the model kept using spaces even with the directly conflicting `indent-tabs` rule still active. Part 1's original hand-built pilot reported the opposite: this exact mutation was the *one* trial that got killed, offered there as the clean illustration of "the skill has something to add specifically because the model has no strong prior either way." `text-styling`'s red/30px branch shows the same reversal: killed in Part 1, survived intact in Sample 2 (`color: red; font-size: 30px;` appeared with no instruction present at all). Read together with the compliance swing above, this is a second, independent demonstration that single-sample mutation verdicts from this pipeline's early runs shouldn't be treated as settled facts about the model — they're one draw from a distribution, same as compliance.

### A hint that skill count itself matters, from an unplanned config change

The same day Sample 2 was collected, the original 6-skill pilot set (`text-styling`, `indent-tabs`, `indent-spaces`, `commit-messages`, `error-handling`, `docstring-style`) got its own accidental natural experiment. Those six never needed the preload-list fix above — they were already correctly configured — so nobody reran them when the fix went in, and their own comparison point predates it: 6 skills in context, versus all 25 for Sample 2. Compared across that unplanned change rather than a controlled rerun, compliance on those six skills moved from 88.2% (15/17) down to 76.5% (13/17) — an 11.7-point drop consistent with a context-dilution effect (more unrelated, simultaneously-loaded skills competing for the same output), the same mechanism visible directly in the `fstring-required`/`string-concat` kills above. One sample under an unplanned config change isn't a controlled test of that hypothesis, but it's a second, independent hint that skill count itself, not just which sample you draw, is a variable this pipeline hasn't yet controlled for.

### Process notes: the "narrates instead of finishing" failure mode isn't text-styling-specific

`t_constant_naming`'s worker output, in the original attempt, appended a "notes on how the invoked skills shaped this" section narrating its own skill usage — `lsc-worker`'s instructions explicitly say the final message should contain nothing but the artifact. Sample 2 saw a related but distinct failure on the same task: two consecutive degenerate attempts (unfinished tool-call traces, not a finished artifact) before a third succeeded — direct, if partial, confirmation that `t_constant_naming` is a recurringly unstable task, even though the specific failure shape differs draw to draw. Part 2/3 scoped the "describes a tool call without the call finishing" failure to the three `text-styling` heading tasks specifically; Sample 2 saw the same shape on `t_code_mixed` too, which touches neither `text-styling` nor file-lookup — a general trait of this subagent configuration under slower, multi-step tasks, not something specific to any one skill's domain. `t_red_unretrieved` reproduced its own version of the pattern for a fourth and fifth time across two live runs now (Part 3 counted two of three; Sample 2's `with_skill` run and its mutation-trial retry both degenerated again) — every attempt at that specific prompt across both live runs has gone looking for an existing heading component instead of emitting CSS directly, worth treating as a stable property of that exact prompt phrasing rather than a coin flip. One `t_measurement_units` attempt also hit a spurious API safety-classifier timeout on a fully benign prompt, unrelated to content — resolved on retry, noted here only because it's a new failure category not seen before.

### Limitations added by this part

The fight/align predictions were the paper author's own guesses at what a model's pretrained default would be, not independently validated — `em-dash-ban`, and the fight-predicted group as a whole once Sample 2 came in, turned out less clean than expected. The new conflict pairs (`line-length-limit` vs. several other character-count instructions) look topically spurious on inspection — a second, larger data point for the pilot's existing "conflict detector only validated on planted cases" limitation, not yet root-caused. Every "which instruction is killed" and "which skill has 0%/100% compliance" claim anywhere in this document should be read as one sample, not a settled measurement — Sample 1 vs. Sample 2's direct, controlled comparison shows compliance can swing over 40 points on identical config, and the mutation-verdict reversals above show the same is true of mutation-adequacy. Multiple independent samples per eval, not a bigger skill count, looks like the more urgent next step for trusting any specific per-key number in this pipeline. Separately: an early draft of this section conflated Sample 2's genuinely-controlled 19-skill comparison with the confounded 6-skill one under a single "iteration-2 vs iteration-3" label before catching the difference — a standing reminder to check, before reporting any future rerun as a controlled comparison, whether every workspace involved actually shares the same tooling/config at both timestamps, not just the same iteration-number scheme.

### Next steps

1. Mutation-test `Fail`-verdict units too, or otherwise stop treating compliance-failure as disqualifying for mutation-adequacy — the current gate hides exactly the cases this part surfaced, and how much it hides changes sample to sample.
2. Run several independent samples per eval (not just a bigger skill/task count) before trusting any single compliance or mutation verdict at the per-key level.
3. Re-verify Part 1's "spaces have no strong pretrained default so the skill has something to add" story now that the same mutation didn't kill on a second independent draw — either sample more, or retire that specific claim.
4. Design a real, controlled test of the context-dilution hypothesis above — rerun the same 6-skill-context task, unmodified, at both 6-skill and 25-skill preload, with several samples each, rather than relying on two data points that differ in both context size and calendar time.
5. `t_red_unretrieved` is 5-for-5 degenerate now across two live runs — worth treating as a real property of that prompt (an empty working directory framed like a real dev task) rather than continuing to sample it hoping for convergence.
