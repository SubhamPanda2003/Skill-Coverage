# Proposed Methodology: Layered Skill Coverage (working title)

*Drafted 2026-09-12, following [literature-review.md](literature-review.md) §4. Working name "Layered Skill Coverage (LSC)" is a placeholder — rename freely.*

## 0. One-paragraph summary

LSC measures skill test adequacy the way Skill Coverage ([arXiv:2606.20659](https://arxiv.org/abs/2606.20659)) does — trajectory-based, aggregated across an eval suite, human-reviewable — but differs in four load-bearing ways: (1) constraint units are **extracted verbatim** (offsets into the source, never paraphrased) instead of rewritten into EARS form; (2) exposure is unpacked into a **three-stage funnel** — *instantiated* (did any task's context ever trigger the condition), *retrieved* (was the skill section actually loaded into the agent's context under progressive disclosure), and *complied* (was the behavior satisfied) — rather than the two-state covered/Pass-Fail scheme already implicit in Skill Coverage's own labels. Note the correction: a plain exposure/compliance split by itself is *not* new — Skill Coverage's `covered`/`verdict` labels already contain that distinction, they just don't report it as two headline numbers. The **retrieved** stage is the genuinely new axis, since Skill Coverage's single-document model can't tell "the agent never even saw this instruction" apart from "the agent saw it and ignored it"; (3) each constraint is tagged **Verifiable or Judged** at segmentation time, so a deterministic assertion replaces the LLM judge wherever the expected behavior maps to a checkable artifact; (4) a **mutation-adequacy** check — arguably the strongest and most time-sensitive claim in this proposal, since it's a short, obvious next step for labs already working on coverage/mutation testing for AI systems (see the novelty discussion) — tests whether the eval suite would actually notice a corrupted instruction, fully automated on the Verifiable subset.

## 1. Design goals

Each goal maps to a gap from the literature review:

| Goal | Literature gap addressed |
|---|---|
| No paraphrase drift in extracted constraints | Skill Coverage requires human audit specifically because EARS rewriting can distort meaning |
| Separate "never exercised" from "exercised but failed" | Skill Coverage's single covered/Pass/Fail collapses two different failure modes into one signal |
| Minimize LLM/human involvement to the subset that truly needs judgment | No existing framework classifies constraints by whether a deterministic oracle is possible |
| Detect whether the eval suite would notice a broken instruction, not just whether it was touched | Coverage generally, not just here, is known to be necessary but not sufficient (same critique as code coverage vs. mutation testing) — unaddressed in every paper surveyed |

## 2. Terminology

- **Skill document `S`** — the raw, unedited text of a `SKILL.md` (or equivalent) file.
- **Constraint unit `u_i = (span_i, type_i)`** — a contiguous, self-contained substring of `S`, identified by exact character offsets `span_i = (start, end)`, such that `extracted_text(u_i) == S[start:end]` always holds (enforced programmatically, never an LLM-generated string).
- **Branch pointer `p_i,k`** — an offset range *within* `u_i` marking one conditional branch (e.g., the "red" half of a compound if/else sentence), used for fine-grained reporting without ever slicing `u_i` itself out of context.
- **Type tag** — `Verifiable` if the unit's expected behavior maps to a checkable artifact property (a literal value, API call, file content, specific action); `Judged` otherwise (style, tone, reasoning-quality, or anything with no mechanical check).
- **Eval suite `T = {t_1 … t_m}`**, each producing a trajectory `τ_j`.
- **Applicability `A(u_i, τ_j)`** — returns the branch pointer(s) whose condition is instantiated by task `j`'s context, or `∅` if the condition never arose. This is a fact about the *task suite's design* — it does not require that the agent ever actually saw the corresponding text.
- **Instantiated(`u_i`)** — `1` iff `∃ j : A(u_i, τ_j) ≠ ∅` (the eval suite tried to trigger this unit at least once, whether or not the agent noticed).
- **Retrieved(`u_i`, `τ_j`)** — `1` iff, for a task where `A(u_i,τ_j) ≠ ∅`, the trajectory evidence shows the chunk of `S` containing `u_i` was actually loaded into the agent's context — logged directly from the progressive-disclosure loader where the harness exposes it, or inferred from citation/quotation evidence in the trajectory otherwise (weaker; see §7).
- **Exposed(`u_i`)** — `1` iff `∃ j : A(u_i,τ_j) ≠ ∅ ∧ Retrieved(u_i,τ_j) = 1` — the condition arose *and* the agent actually had the instruction in view. This, not `Instantiated`, is the real precondition for a compliance verdict to mean anything.
- **Verdict(`u_i`, `τ_j`) ∈ {Pass, Fail}`** — defined only when `Exposed` holds for that `(u_i,τ_j)` pair.

## 3. Pipeline

### Stage 1 — Deterministic segmentation
Parse `S` structurally: markdown list items, table rows, and code blocks are atomic units by construction; prose paragraphs are split with a rule-based sentence splitter. A fixed trigger-word linter (pronouns — "it", "this", "that", "they"; ellipsis markers — "same", "otherwise", "respectively"; clause-joining conjunctions — "and if…", "or if…", "but if…") flags candidate boundaries that would create a dangling reference, and the splitter **fails closed**: on any trigger, merge backward into the enclosing unit rather than cut. Worst case this produces coarser (larger) units, never a referentially broken fragment. No LLM call in this stage; output is reproducible byte-for-byte given the same file.

### Stage 2 — Type classification
A rule-based check scans each unit for a concrete, checkable token (a number+unit, a literal string, a named API/function, a file path, a specific flag). Present → `Verifiable`. Absent → `Judged`. This is a lint pass, not a semantic judgment call — same input, same tag, every run.

### Stage 3 — Task authoring
Eval tasks are (where possible) authored to reuse the skill's own condition vocabulary, so applicability can be matched lexically rather than semantically. This is a controlled-benchmark choice, not a claim that all real-world tasks will cooperate — see §7.

### Stage 4 — Instantiation, retrieval logging, and applicability
**Instantiation:** deterministic keyword/regex match against the task description first; fall back to an LLM applicability check only when lexical match is inconclusive. Every fallback firing is logged, so the size of the "needed a model" bucket is itself a reported statistic, not hidden inside an opaque pipeline.

**Retrieval (the new axis):** independently of instantiation, instrument the skill runtime's progressive-disclosure loader to log which chunks of `S` were actually pulled into the agent's context per task — a pure logging hook, fully deterministic, no model call. Where the harness doesn't expose loader internals (a closed agent product), fall back to scanning the trajectory for direct quotation/citation of the chunk as weaker, inferred evidence of retrieval, flagged as such rather than treated as a logged fact. This is what turns "the condition arose" into "the agent actually had a chance to comply" — see the `Retrieved` definition in §2.

### Stage 5 — Compliance evaluation
- **Verifiable units:** a literal assertion against the trajectory's final artifact (file diff, tool-call parameters, output string) — e.g. `assert "font-size: 30px" in artifact`. Pure function, fully reproducible, no model call.
- **Judged units:** LLM-as-judge given `(u_i, active branch pointer, trajectory evidence)`, required to ground its verdict in a cited piece of evidence — same discipline Skill Coverage uses. The judge's reliability is validated **once** against a human-labeled sample (report κ agreement, as Skill Coverage did — 0.770/0.695 was their number), not re-audited per verdict thereafter.

### Stage 6 — Coverage computation
Two headline numbers, reported separately (not collapsed into one):

```
TaskSuiteCoverage  = |{u_i : Instantiated(u_i) = 1}| / |U|
RetrievalRate      = |{u_i : Instantiated(u_i)=1 ∧ Exposed(u_i)=1}| / |{u_i : Instantiated(u_i)=1}|
ComplianceCoverage = |{u_i : Exposed(u_i)=1 ∧ ∃j: Verdict(u_i,τ_j)=Pass}| / |{u_i : Exposed(u_i)=1}|
```

This three-stage funnel isolates a different failure mode at each step: a low `TaskSuiteCoverage` indicts the **eval suite** (it never even tried to trigger this instruction); a low `RetrievalRate` at high `TaskSuiteCoverage` indicts the **skill's chunking/progressive-disclosure design** (the suite tried, but the loader never surfaced the instruction to the agent); a low `ComplianceCoverage` at high `RetrievalRate` indicts the **agent** (it saw the instruction and didn't follow it). Skill Coverage's single covered/Pass/Fail signal cannot distinguish the second case from the third — it would score both as a Fail against the agent.

Report `ComplianceCoverage` split further by type tag: `VerifiedCoverage` (computed with zero LLM/human involvement) and `JudgedCoverage` (computed via the validated LLM judge). A reader can then see exactly how much of the headline number rests on a deterministic oracle versus a judged one.

### Stage 6b — Cross-skill conflict coverage
When multiple skills are loaded in the same task (the agentskills.io spec explicitly supports this), their instructions can contradict each other on the same condition — e.g. one skill says "always use tabs," another says "always use spaces." No prior work in the reviewed literature evaluates a single skill in the context of others being loaded simultaneously; this stage is a genuinely new problem framing, not just a new metric for an existing one.

**Detection:** two `Verifiable`, unconditional units from *different* skills are flagged as a conflicting pair if their topical keywords overlap (same subject matter) but the concrete checkable tokens they assert are disjoint (e.g. "tabs" vs. "spaces"). This is a heuristic validated against one deliberately-planted case (§ pilot results), not a general semantic conflict detector — treat it as a starting point, not a completeness claim.

**Metrics**, computed only over tasks where both units in a pair are `Exposed` simultaneously:
```
ConflictInstantiatedRate  = |{pairs with >=1 task exposing both}| / |detected pairs|
ConflictResolutionRate    = |{task instances where the artifact is internally consistent}| / |{task instances where the conflict is instantiated}|
```
`ConflictResolutionRate` asks a different question than raw compliance: not "did the agent satisfy both instructions" (impossible by construction when they contradict), but "did the agent pick one and apply it consistently, rather than producing an internally inconsistent artifact (e.g. mixed tabs and spaces in the same file)." A conflicting pair will always show 0% compliance for whichever instruction loses — that's expected and uninformative; resolution consistency is the metric that actually distinguishes a well-behaved agent from a poorly-behaved one under conflicting skills.

### Stage 7 — Reporting
Render `S` unmodified with gutter highlighting: gray = never exposed, yellow = exposed + Fail, green = exposed + Pass — at the branch-pointer level where available, unit level otherwise. Because every unit is a verbatim span with real offsets, this is a mechanical rendering step, not a reconstruction.

**Required, not optional: always report per-task detail alongside the aggregate.** The pilot (see [results.md](results.md)) caught this the hard way — an aggregate per-unit rollup that takes the best verdict across all tasks touching a constraint ("Pass if any task ever passed") will silently mask a genuine per-task `Unretrieved` gap whenever a *different* task happens to retrieve and pass the same constraint. `RetrievalRate` read 100% in the pilot despite a deliberately unretrieved case existing in the data — only the per-task table revealed it. This is the same "collapsed signal hides the diagnosis" failure this proposal criticizes Skill Coverage for (§0); a per-key-only report reintroduces it. Ship both views, always.

### Stage 8 — Mutation-adequacy check (Verifiable subset only, fully automated)
For each `Verifiable` unit that was exposed by at least one task with a deterministic verifier: produce a mutant skill `S'_i` with that unit's span deleted or corrupted, rerun the same tasks against `S'_i`, and check whether any previously-Pass verifier now fails.

```
MutationKilled(u_i) = 1 if ∃ j : Verdict(u_i, τ_j | S) = Pass ∧ Verdict(u_i, τ_j | S'_i) = Fail
MutationScore = |{u_i : MutationKilled(u_i) = 1}| / |{u_i : Verifiable ∧ Exposed(u_i) = 1}|
```

A low mutation score on units that already show high compliance coverage is a specific, actionable signal: the eval suite touches the instruction but wouldn't notice if it were deleted — i.e., the instruction is either redundant or under-tested by the *outcome* checks, even though it's "covered."

### Stage 9 — Coverage-guided strengthening (optional, reuses Skill Coverage's idea)
Fail-verdict units drive a rewrite that only re-emphasizes existing wording (checklists, ordering, verification gates) — same discipline as the original paper, now scoped to the specific branch pointer rather than a paraphrased constraint.

## 4. Worked example (the running font-size case)

Source sentence in `S`:
> "If the color of the text is blue then change the font to 20px and if color is red then change it to 30 px."

- **Segmentation:** the linter sees "and if" (conjunction) + "it" (pronoun) inside the second clause → fails closed → keeps the **entire sentence** as one unit `u_1`, with two branch pointers: `p_blue` = "the color of the text is blue then change the font to 20px", `p_red` = "color is red then change it to 30 px".
- **Type:** contains literal values ("20px", "30 px") → `Verifiable`.
- **Tasks:** `t_blue` ("make the heading text blue"), `t_red` ("make the heading text red").
- **Applicability:** keyword match → `A(u_1, τ_blue) = p_blue`, `A(u_1, τ_red) = p_red`. Both branches exposed.
- **Compliance:** deterministic assertion checks the final artifact for `font-size: 20px` under `τ_blue` and `font-size: 30px` under `τ_red`.
- **Report:** the full sentence renders once, untouched; `p_red` highlights green if `τ_red`'s assertion passed, `p_blue` independently green/yellow based on `τ_blue`. If the eval suite only ever included `t_red`, `p_blue` stays gray — visibly flagging "the blue branch of this instruction has never been tested" without ever fragmenting or rewording the source.
- **Mutation check:** delete `u_1` entirely, rerun `t_red` — if the font-size assertion still happens to pass (e.g. 30px was already the CSS default), `MutationKilled(u_1) = 0` despite `u_1` showing 100% compliance coverage, correctly flagging that the eval suite doesn't actually prove this instruction matters.
- **Retrieval variant (the new axis):** suppose `u_1` lives inside a section titled "Advanced Styling," and the skill runtime's progressive-disclosure loader only pulls that section into context when the task text contains a styling-related trigger word. Task `t_red` = "make the heading red" instantiates the red branch (`A(u_1,τ_red) = p_red`) but never says "styling," so the loader never retrieves the section: `Retrieved(u_1,τ_red) = 0`. Under Skill Coverage's model this pair already counts as `covered` (the condition was instantiated) and would receive a Fail verdict if the agent guesses the wrong font size — silently blaming the *agent* for a failure actually caused by the *skill's own chunking*. Under LSC: `Instantiated(u_1)=1`, `Exposed(u_1)=0` — correctly surfaced as an **Unretrieved** gap pointing at the section-triggering design, not agent compliance.

## 5. Comparison to prior work

| | Skill Coverage (2606.20659) | Scale-Eval framework (2606.17819) | **This proposal (LSC)** |
|---|---|---|---|
| Constraint form | EARS-normalized (rewritten) | Hidden rubric (rewritten) | Verbatim span (never rewritten) |
| Granularity | Whole constraint | Whole skill (aggregate score) | Constraint + sub-branch pointer |
| Exposure model | Binary: instantiated-or-not (covered) | Binary: rubric applicable-or-not | Three-stage funnel: instantiated → retrieved → complied |
| Coverage signal | Single covered/Pass/Fail | Single delta score | TaskSuiteCoverage / RetrievalRate / ComplianceCoverage, reported separately |
| Oracle | LLM judge for all constraints | LLM judge for all rubrics | Deterministic assertion where possible, LLM judge only for the rest |
| Audit burden | Human audit of every extracted constraint (fidelity) | Rubric design audit | One-time parser validation + one-time judge-agreement check, not per-item |
| Adequacy beyond coverage | Not addressed | Not addressed | Mutation-adequacy score on the Verifiable subset |

## 6. What still genuinely requires judgment (honesty section)

- **Applicability matching** for tasks phrased outside the skill's own vocabulary still needs an LLM fallback — this is logged and bounded, not eliminated.
- **Compliance on `Judged`-tagged units** (tone, reasoning quality, anything without a checkable artifact) has no deterministic substitute — the LLM judge (validated once via human-agreement sampling) is unavoidable here, same as in Skill Coverage.
- **Segmentation quality** depends on the trigger-word linter's coverage of anaphora patterns; it will over-merge on patterns not in the word-list (safe failure — coarser units) but could under-merge on an unanticipated pattern (unsafe failure — worth a validation pass against a sample corpus before trusting it at scale).
- **Retrieval detection on closed harnesses.** When the agent product doesn't expose progressive-disclosure loader internals, `Retrieved()` degrades from a deterministic log read to inferred evidence from trajectory citations — which itself may need occasional human/LLM adjudication, the same caveat as the `Judged` compliance tier.

## 7. Threats to validity to disclose in the preprint

- **External validity:** controlled, skill-vocabulary-matched task authoring (Stage 3) improves determinism but may not reflect how real users phrase tasks — report both a "controlled vocabulary" and a "free-form" task condition and compare applicability-fallback rates between them.
- **Construct validity:** `VerifiedCoverage` is only as good as the type-classification linter's ability to spot checkable tokens — false negatives (a checkable instruction misclassified as `Judged`) would understate how deterministic the pipeline actually is; worth a manual spot-check of the classifier on a sample.
- **Mutation-adequacy cost:** one mutant + rerun per exposed Verifiable unit scales linearly with skill size and task-suite size; report wall-clock/token cost alongside the score, as SkillsBench-scale evaluation already needs to track cost per the industry gap noted in the survey.
- **Retrieval axis only adds information where progressive disclosure exists.** If a harness loads the whole skill file wholesale on every task (no chunking), `Retrieved(u_i,τ_j)` is trivially `1` whenever `Instantiated` is `1`, and the funnel collapses back to Skill Coverage's two-stage model. Report which harnesses in the evaluation actually implement partial/progressive loading — the retrieval axis is only a meaningful contribution for those.

## 8. Evaluation plan for the preprint

1. Run the full pipeline over SkillsBench's skill/task set; report `TaskSuiteCoverage`, `RetrievalRate`, and `ComplianceCoverage` per agent/model, and compare `TaskSuiteCoverage` against Skill Coverage's published 38.66–45.51% numbers as an external sanity check (expect them to be in a similar range, since `Instantiated` is the same condition their single coverage metric already captures). If SkillsBench's harnesses turn out to load skills wholesale rather than progressively, `RetrievalRate` will report as trivially ~100% — itself a useful finding, and grounds for testing the retrieval axis on a harness that does implement progressive disclosure instead.
2. Report the `Verifiable` vs `Judged` split size across the SkillsBench skill corpus — this number alone is a useful headline result ("X% of real-world skill instructions are mechanically checkable").
3. Run the one-time human-agreement study on the `Judged` subset only (smaller sample than auditing everything, directly comparable to Skill Coverage's κ=0.770/0.695 baseline).
4. Run the mutation-adequacy check on the `Verifiable` subset and report the distribution of `MutationScore` against `ComplianceCoverage` — the interesting result is any unit with high compliance coverage but low mutation score, since that's a new failure mode this framework can surface and Skill Coverage cannot.
5. Ablate Stage 3 (controlled vs. free-form task vocabulary) to report how much determinism you lose when tasks aren't authored with the skill's vocabulary in mind — this quantifies the real cost of the "no human audit" claim.

## 9. Naming and next steps

"Layered Skill Coverage" is a placeholder — happy to workshop a name once the empirical results are in and you know which finding is the headline (the Verified/Judged split, the instantiated/retrieved/complied funnel, or the mutation-adequacy result would each suggest a different framing/title).

**A pilot implementation now exists** — see [results.md](results.md) for the full write-up. It's a pipeline-validation run against hand-constructed trajectories (no live LLM agent was available in that environment), not an empirical study of real agent behavior, but it did already surface one real design flaw (the per-key aggregate rollup masking a genuine `Unretrieved` case — now fixed by always reporting per-task detail alongside the aggregate, see Stage 7) and confirmed the mutation-adequacy and conflict-coverage mechanisms produce the intended diagnostic separation on known cases.

**Sequencing note given the novelty/scoop-risk discussion:** mutation-adequacy (Stage 8) is the component most likely to be independently reinvented soon, since it's a short, obvious hop for labs already fluent in mutation/coverage testing for AI systems (e.g. Skill Coverage's own co-author works in that space). If timeline is a concern, prioritize a minimal Stage 8 implementation first — it can run directly on SkillsBench's existing deterministic verifiers without waiting on the full extractive-segmentation pipeline (Stages 1–3) — over polishing the lower-risk components. Otherwise, the standard build order applies: a small pilot on 5–10 SkillsBench skills, running Stages 1–2 hand-in-the-loop to validate the linter and classifier before investing in full automation.
