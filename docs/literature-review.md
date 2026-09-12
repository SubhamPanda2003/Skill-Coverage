# Literature Review: Test Adequacy and Coverage for LLM Agent Skills

*Compiled 2026-09-12. Scope: academic work on evaluating, benchmarking, and measuring coverage/adequacy of "agent skills" (reusable natural-language procedural artifacts for LLM agents), plus the current industry state of skill validation.*



---

## 1. Background

"Agent Skills" are packaged, reusable instructions (typically a `SKILL.md` plus optional scripts/resources) that extend an LLM agent's behavior at inference time without fine-tuning. Anthropic published the **Agent Skills Specification** as an open standard at [agentskills.io](https://agentskills.io) (Dec 18, 2025), and it has since been adopted across Claude Code, OpenAI Codex, GitHub Copilot, Cursor, Gemini CLI, VS Code, and others (~40 compatible products as of mid-2026). This rapid, cross-vendor adoption — with no shared method for testing what a skill actually does to agent behavior — is the gap the surveyed papers are responding to.

## 2. The Landscape

### 2.1 Outcome / utility benchmarks — "does the skill help at all?"

**SkillsBench** ✅🔍 (Li, Chen, Liu et al., [arXiv:2602.12670](https://arxiv.org/abs/2602.12670), Feb 2026) is the closest thing to a de facto standard. It pairs curated skills with hand-authored tasks and deterministic (unit-test-style) verifiers — 87 tasks across 8 domains in the original release (later cited elsewhere as 202 task-linked skill artifacts / 11 domains / 7,308 trajectories, suggesting the benchmark grew across revisions — reconcile version numbers before citing). Headline result: curated skills raise average pass rate from 33.9% → 50.5% (+16.6 pp). This is an **outcome metric**: it tells you a skill helped, not which of its instructions were exercised or followed.

**A Framework for Evaluating Agentic Skills at Scale** ✅ (Shaposhnikov, Fortuin, Stipcich, Gorinova, Heineike, Willoughby, [arXiv:2606.17819](https://arxiv.org/abs/2606.17819)) scales this idea to ~1,000 synthetically generated tasks from 500 real-world skills, scoring each on two rubric-based axes — **instruction-following** and **goal-completion** — via LLM-as-judge, and reporting a "skill delta" (with vs. without skill access). Findings: skills lift performance mainly through instruction-following (~+5.2 pts average), not correctness (which saturates near 90% regardless); gains vary sharply by domain (+38.1 pts for media/file processing vs +16.7 for testing/QA) and let weaker/cheaper open-weight models match frontier-tier scores. This is closer to coverage in spirit (it separates "followed instructions" from "got the right answer") but still reports an aggregate score per skill, not a per-instruction covered/uncovered breakdown.

### 2.2 Test adequacy / coverage — "which parts of the skill were actually exercised?"

**Skill Coverage: A Test Adequacy Metric for Agent Skills** ✅ (Tan, Sun — Mohamed bin Zayed University of AI; Huang — University of Liverpool, [arXiv:2606.20659](https://arxiv.org/abs/2606.20659)) is the central paper for this project and, as far as this review found, the **only** work that explicitly imports classical test-adequacy theory (Weyuker's coverage axioms, EARS requirements normalization, the oracle/"checked coverage" problem) into the skill-evaluation space.

Pipeline:
1. **Constraint extraction** — LLM-assisted, human-audited extraction of skill prose into EARS-normalized **skill behavior constraints (SBCs)**: *"When ⟨applicability condition⟩, the agent shall ⟨observable behavior⟩."*
2. **Trajectory labeling** — for each (constraint, trajectory) pair: is the condition instantiated at all (**covered** vs not)? If covered, did the agent's observable behavior satisfy it (**Pass**) or violate/omit it (**Fail**)? Verdicts must be grounded in concrete trace evidence (tool calls, file state, command output, artifacts).
3. **Coverage-guided strengthening** — Fail-labeled constraints drive a targeted rewrite of the skill (checklists, ordering, verification gates) that only re-emphasizes existing instructions, without adding new solution content.

Coverage is defined as the fraction of all (constraint, trajectory) pairs that received *any* verdict (Pass or Fail) — i.e., were exercised at all — over the full constraint set.

Key results on SkillsBench, across 5 agent/model configurations (Codex/GPT-5.5, Claude Code/Opus 4.7, OpenHands × {DeepSeek V4 Pro, DeepSeek V4 Flash, GLM 5.1}):

| Agent / Model | Task success | SBC coverage |
|---|---|---|
| Codex / GPT-5.5 | 53.26% | 43.60% |
| Claude Code / Opus 4.7 | 52.87% | 38.66% |
| OpenHands / DeepSeek V4 Pro | 40.23% | 45.51% |
| OpenHands / GLM 5.1 | 37.55% | 41.64% |
| OpenHands / DeepSeek V4 Flash | 32.95% | 43.73% |

i.e., **over half of documented skill behavior is never even exercised** in standard benchmark runs, regardless of task success rate. Coverage-guided strengthening recovered an average of 16.0% of previously failed tasks (up to 30.7% for Codex/GPT-5.5). LLM-judge vs. human agreement was acceptable but below human-human ceiling (κ=0.770 vs κ=0.961 on the coverage denominator).

The authors' own **threats-to-validity** section already flags several of the gaps below: judge/trace validity (LLM judge can miss or misjudge evidence), reliance on *visible* evidence only, and narrow external validity (1 benchmark, 87 tasks, 5 agent/model pairs, no independent skill collection).

### 2.3 Skill generation & continual learning — "how do skills get created/improved, and how is *that* measured?"

- **SkillLearnBench** 🔍 ([arXiv:2604.20087](https://arxiv.org/abs/2604.20087), accepted COLM 2026) — first benchmark for continual-learning methods that auto-generate skills from agent experience; 20 tasks / 15 sub-domains; evaluates at skill-quality, trajectory, and outcome levels. Finding: all continual-learning methods beat no-skill baselines, but no method dominates and stronger base LLMs don't reliably help — i.e., skill-generation quality doesn't obviously scale with model strength.
- **SkillGenBench** 🔍 ([arXiv:2605.18693](https://arxiv.org/abs/2605.18693)) — benchmarks skill-*generation pipelines* themselves (as opposed to the resulting skill's downstream effect).
- **CASCADE** 🔍 ([arXiv:2512.23880](https://arxiv.org/abs/2512.23880), Huang, Dec 2025) — cumulative/autonomous skill creation and evolution for scientific-research agents; adjacent to evaluation but framed around accumulation, not adequacy testing.
- **"What Should a Skill Remember?"** 🔍 ([arXiv:2606.09421](https://arxiv.org/abs/2606.09421)) — quality/cost tradeoffs in cost-aware skill rewriting; relevant if a coverage framework wants to report a cost axis alongside coverage.
- **"From Raw Experience to Skill Consumption"** 🔍 ([arXiv:2605.23899](https://arxiv.org/abs/2605.23899)) — systematic study of model-generated agent skills.

### 2.4 Retrieval / routing — "does the agent pick the right skill?"

- **SkillResolve-Bench** 🔍 (Ding, Huawei, [arXiv:2606.10388](https://arxiv.org/abs/2606.10388)) — measures and resolves ambiguity when multiple skills cover overlapping capabilities, a retrieval-time problem rather than a within-skill coverage problem.
- The survey below also references **SRA-Bench** / **SkillRouter** for retrieval-accuracy evaluation (not independently verified in this pass).

### 2.5 Safety / security auditing

- **SkillSafetyBench** 🔍 ([arXiv:2605.12015](https://arxiv.org/abs/2605.12015)) — evaluates agent safety under skill-facing attack surfaces (e.g., a malicious or compromised skill file).
- **Snyk "ToxicSkills"** (industry, not peer-reviewed) — audited 22,511 public skills, found prompt-injection risk in ~36% of tested skills (~6.3 issues/skill on average). This is the most mature *deployed* validation practice in the ecosystem today, but it targets security, not behavioral coverage.
- The survey (§2.6) additionally names **SKILL-INJECT** as a benchmark for detecting malicious/harmful skills.

### 2.6 Surveys

**Agent Skill Evaluation and Evolution: Frameworks and Benchmarks** ✅ (Ding, Zhou, Jin, Tong, Zhou, Metaxas — Rutgers/UNC Charlotte, [arXiv:2606.11435](https://arxiv.org/abs/2606.11435)) categorizes the space into six benchmark types (utility, generation, retrieval/routing, safety-auditing, SWE-specific, real-world-environment) and explicitly concludes that:
- evaluation today is **"predominantly binary (pass/fail)"**, without latency, token-cost, or error-type granularity;
- there is **no longitudinal evaluation** tracking a skill's quality across edits/feedback rounds;
- multimodal/embodied skill evaluation is largely unaddressed.

This survey does **not** discuss coverage as a concept at all — reinforcing that Skill Coverage (§2.2) is addressing a gap the survey's own authors didn't have a name for yet.

### 2.7 Industry practice (non-academic)

- **SkillsBench** functions as the closest thing to an industry-referenced benchmark (Stanford/CMU/Berkeley/Oxford/BenchFlow involvement lends it more legitimacy than a single-lab benchmark).
- **Marketplace-level curation is ad hoc and non-standardized**: Anthropic's official skills directory uses manual curation; third-party directories (e.g., Agensi) run their own bespoke security scans; others (e.g., SkillHub) use an AI-evaluated quality score. No shared schema, lint tool, or CI check is used across the ~40 agentskills.io-compatible products.
- No production tool analogous to code-coverage instrumentation (Istanbul, JaCoCo, coverage.py) exists for skills — i.e., there is no "run this and get a coverage report" tool a skill author can currently use before publishing.

## 3. Gap Analysis

Ranked roughly by how directly they open room for new, publishable work:

1. **Single-paper, single-benchmark validation.** Skill Coverage's own threats-to-validity section admits the metric has only been validated on one benchmark (SkillsBench), 87 tasks, 202 artifacts, 5 agent/model pairs. There is no cross-benchmark replication (e.g., against SkillLearnBench's task set, or a from-scratch skill collection) to show the metric generalizes rather than overfitting to SkillsBench's task style.
2. **No lightweight/automated constraint-extraction pipeline.** The current pipeline requires human-authored few-shot demonstrations and human audit of LLM-extracted constraints per skill. There's no evaluated fully-automatic extractor, no measurement of extraction cost vs. benchmark size, and no study of how extraction quality degrades on noisier, less-curated (i.e., realistic marketplace) skills rather than SkillsBench's top-quartile curated set.
3. **No standardized constraint schema across tools.** Skill Coverage uses EARS-style SBCs; the Scale-evaluation framework (§2.1) uses hidden rubrics; SkillsBench uses unit-test verifiers. Nothing unifies these into an interchange format, so coverage numbers from different tools/papers aren't comparable — analogous to the pre-standardization era of code coverage before formats like LCOV existed.
4. **Coverage is binary/exercised-or-not; no partial or weighted coverage.** A constraint counts as "covered" the moment it's exercised once, regardless of how many of its edge cases or applicability-condition variants were hit. There's no analogue of branch/path coverage — e.g., a conditional instruction ("if X do A, else do B") is covered by hitting *either* branch once.
5. **No compositional / cross-skill coverage.** If a skill invokes or depends on another skill (common in the Anthropic spec's model, where skills can reference sub-skills or shared scripts), no existing metric addresses coverage of the *composed* behavior graph — only single-skill, single-trajectory pairs are covered in current work.
6. **No treatment of bundled non-text artifacts.** Skill packages under the Anthropic spec bundle scripts and resources, not just prose. Skill Coverage's constraint extraction is scoped to natural-language instructions; executable code shipped inside a skill package has no coverage treatment (this is where classical code coverage tools could plug in but currently don't).
7. **No coverage-driven test generation loop.** The Skill Coverage paper explicitly flags this as future work: uncovered constraints are natural targets for synthesizing new tasks that would exercise them, but no implementation exists yet — this is an open, concretely-scoped contribution opportunity.
8. **No cost-normalized coverage.** Achieving high coverage (more/longer trajectories, more elaborate tasks) has a token/dollar cost. "What Should a Skill Remember?" studies cost-aware skill *rewriting* but nothing yet reports coverage-per-token or coverage achieved at fixed budget — relevant since the survey (§2.6) flags cost/latency as a missing evaluation axis industry-wide.
9. **No longitudinal/regression coverage tracking.** The survey (§2.6) flags that no benchmark tracks a skill's evaluation across successive edits. A "coverage regression" check (did this skill edit reduce coverage of previously-passing constraints?) is unaddressed and maps directly onto a familiar software-engineering pattern (coverage diffing in CI).
10. **No public tooling / open dataset of coverage-annotated trajectories.** Unlike code coverage (mature open-source tooling across every language), there is no released, reusable coverage-instrumentation tool or shared annotated-trajectory dataset an outside researcher could build on directly — Skill Coverage's constraint sets and labeled trajectories are not stated to be public in the summarized material available here (verify against the paper's data-availability statement).
11. **No cross-agent-harness normalization.** Coverage numbers are computed over observable trajectory evidence, but trajectory formats/tooling differ across Claude Code, Codex, OpenHands, etc. There's no study of whether coverage as measured is an artifact of what a given harness happens to log/expose, versus true agent behavior.
12. **Safety and coverage are currently disjoint.** SkillSafetyBench / Snyk's ToxicSkills address malicious or vulnerable skill content; Skill Coverage addresses whether legitimate instructions are followed. No work asks whether *uncovered* constraints correlate with higher safety risk (an untested instruction is also an unverified one).

## 4. Where a New Framework Could Sit

The clearest, most defensible angles for a new contribution (each maps to one gap above) are:
- **Cross-benchmark / cross-collection validation** of a coverage metric (gap 1) — lowest novelty but highest immediate credibility, since it directly answers the original authors' stated limitation.
- **Coverage-driven test generation** (gap 7) — the original paper names this outright as unimplemented future work, so there's no priority conflict, and it has a clean evaluation story (does synthesized-task coverage-closing actually raise task success?).
- **A structural/weighted coverage criterion** (gap 4) — analogous to branch coverage vs. statement coverage in software testing, this is a natural theoretical extension with a clear "why is exercised-once insufficient" motivating example.
- **Open tooling + interchange format** (gaps 3, 10) — less of a "novel metric" paper and more of a systems/infrastructure contribution (could still be arXiv-appropriate, especially paired with an empirical study).

This is scoping, not a decision — happy to go deeper on any one of these (e.g., draft a formal definition, a minimal viable pipeline, or a related-work table by exact citation) once you pick a direction.

**Update:** a concrete proposal combining gaps 4 (weighted/branch coverage), 2 (automated extraction), and a new mutation-adequacy angle has since been drafted in [proposed-methodology.md](proposed-methodology.md).

## 5. Reference List

| Key | Title | Authors | arXiv | Date |
|---|---|---|---|---|
| SkillCoverage26 | Skill Coverage: A Test Adequacy Metric for Agent Skills | Tan, Huang, Sun | [2606.20659](https://arxiv.org/abs/2606.20659) | Jun 2026 |
| SkillsBench26 | SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks | Li, Chen, Liu, et al. | [2602.12670](https://arxiv.org/abs/2602.12670) | Feb 2026 |
| ScaleEval26 | A Framework for Evaluating Agentic Skills at Scale | Shaposhnikov, Fortuin, Stipcich, Gorinova, Heineike, Willoughby | [2606.17819](https://arxiv.org/abs/2606.17819) | Jun 2026 |
| SkillSurvey26 | Agent Skill Evaluation and Evolution: Frameworks and Benchmarks | Ding, Zhou, Jin, Tong, Zhou, Metaxas | [2606.11435](https://arxiv.org/abs/2606.11435) | Jun 2026 |
| SkillLearnBench26 | SkillLearnBench: Benchmarking Continual Learning Methods for Agent Skill Generation on Real-World Tasks | (COLM'26) | [2604.20087](https://arxiv.org/abs/2604.20087) | Apr 2026 |
| SkillGenBench26 | SkillGenBench: Benchmarking Skill Generation Pipelines for LLM Agents | — | [2605.18693](https://arxiv.org/abs/2605.18693) | May 2026 |
| SkillResolveBench26 | SkillResolve-Bench: Measuring and Resolving Same-Capability Ambiguity in Agent Skill Retrieval | Ding (Huawei) | [2606.10388](https://arxiv.org/abs/2606.10388) | Jun 2026 |
| SkillSafetyBench26 | SkillSafetyBench: Evaluating Agent Safety under Skill-Facing Attack Surfaces | — | [2605.12015](https://arxiv.org/abs/2605.12015) | May 2026 |
| OpenSkillEval26 | OpenSkillEval: Automatically Auditing the Open Skill Ecosystem for LLM Agents | — | [2605.23657](https://arxiv.org/abs/2605.23657) | May 2026 |
| CASCADE25 | CASCADE: Cumulative Agentic Skill Creation through Autonomous Development and Evolution | Huang | [2512.23880](https://arxiv.org/abs/2512.23880) | Dec 2025 |
| SkillRemember26 | What Should a Skill Remember? Quality–Cost Trade-offs in Cost-Aware Skill Rewriting for Language Model Agents | — | [2606.09421](https://arxiv.org/abs/2606.09421) | Jun 2026 |
| RawExperience26 | From Raw Experience to Skill Consumption: A Systematic Study of Model-Generated Agent Skills | — | [2605.23899](https://arxiv.org/abs/2605.23899) | May 2026 |

*Rows without a listed author name were not independently confirmed in this pass — pull the author list from the arXiv abstract page before citing.*

---

*Next steps before this goes into a preprint: (1) fully read every 🔍 paper rather than relying on abstracts/snippets, (2) verify all numeric claims in §2.2's table directly against the Skill Coverage PDF tables, (3) check for any 2026-Q3 papers published after this review's compilation date, (4) decide which of the four positioning options in §4 to pursue and re-scope the gap list around it.*
