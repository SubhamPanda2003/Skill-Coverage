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

**Three worker trajectories are degenerate, not genuinely non-compliant.** `t_blue`, `t_red`, and `t_red_unretrieved` (all `text-styling` tasks) show the same broken pattern: the subagent described a bash tool call in its final response text but never actually invoked it (`tool_uses: 0`), and never touched a heading element. `text-styling`'s resulting 0% compliance in this run is an artifact of that failure mode, not evidence the skill was disregarded. This was flagged, not root-caused — see Limitations.

**`commit-messages` also shows 0% compliance, for a different and legitimate reason.** Both commit-message tasks ran in an isolated environment with no git repo or diff to summarize; the worker correctly asked for context rather than fabricating a commit message. Reasonable agent behavior, zero artifact produced, so it fails by construction — a task/environment mismatch, not a skill failure.

**Mutation-adequacy mostly isn't testing what it looks like it's testing yet.** 11 of 12 live trials came back `killed: false` — not because `error-handling` and `docstring-style` are decorative, but because their task prompts already restate the exact requirement in plain English ("raise ... with the original exception chained using `from`", "documenting its parameter, return value, and the exception it can raise"). Deleting the matching skill instruction changes nothing because the task text alone is sufficient to produce compliant output. The one trial that *was* killed — `indent-spaces#u0#b0` on `t_code_mixed` — is the one task generic enough ("format the code with proper indentation") to give the skill instruction something to add: with it deleted, the agent switched to tabs. This is the pilot's "trailing newline" decorative-instruction finding playing out at the scale of an entire task suite rather than one isolated unit, and it means most of today's `MutationScore` denominator isn't a meaningful adequacy test yet.

### Limitations of this run specifically

- N=1 run, one model, no repeated trials — same caveat the pilot gave for its synthetic data, now attached to real output instead.
- The three degenerate `text-styling` trajectories were not rerun or root-caused; whether this is one-off sampling noise or a systematic issue with that task shape is unknown.
- Judged-tier verdicts came from real `lsc-judge` subagent calls this time (progress on the pilot's Next Steps #1), but each is a single, unreplicated judgment — no human-labeled κ-agreement check has been run against them yet.
- `error-handling` and `docstring-style` task prompts are too prescriptive for mutation-adequacy to say anything meaningful about those two skills yet (see above) — they need less-leading phrasing before a second mutation run would be informative.

### Next steps

1. Rewrite the `error-handling`/`docstring-style` task prompts to state the goal without restating the skill's specific mechanism, so mutation-adequacy can actually distinguish load-bearing from decorative instructions for those two skills.
2. Rerun `t_blue`/`t_red`/`t_red_unretrieved` to check whether the degenerate tool-call-as-text pattern reproduces, and if so, root-cause whether it's a task-shape issue or a subagent-harness issue.
3. Run the κ-agreement check called for in the pilot's Next Steps #1, now that real `lsc-judge` verdicts exist to sample against human labels.
