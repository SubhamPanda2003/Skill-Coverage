# LSC Benchmark — Final Report

**What this measures:** not "does the skill help," but whether the model follows each individual instruction inside a `SKILL.md` file once the skill is retrieved. 25 skills, 31 evals, 38 instruction-branches.

## Read this first: two bugs and a noisy result, in order

1. **A configuration bug invalidated the first attempt at the 25-skill scale.** The `lsc-worker` subagent relies entirely on a `skills:` frontmatter preload list to see any skill content at all — it runs with no tools, so it can't look one up at runtime either. That list was written for the original 6-skill pilot and never updated for the 19-skill expansion, so 19 of 25 skills were never actually visible to the worker, even though the pipeline reported 100% retrieval (a topic-keyword proxy, not evidence of real access). The model was generating unguided default output on those 19 skills' tasks, not skill-influenced output. Fixed by adding all 25 skill names to the preload list. That first attempt's numbers (`ComplianceCoverage` 52.8%, `MutationScore` 5%) aren't reported below as data — they're an artifact of the bug.
2. **Two independent, properly-configured samples exist now, one day apart, and they don't agree.** Same 19 skills, same prompts, same fixed config both times — `ComplianceCoverage` on that set moved from 33.3% (7/21) to 76.2% (16/21), a 43-point swing with nothing different between the draws except which sample the model produced. Every specific per-skill number below should be read as one sample from a noisy distribution, not a settled measurement.
3. **A separate config change, landed by accident between those two samples, hit the original 6-skill pilot set too.** Those six (`text-styling`, `indent-tabs`, `indent-spaces`, `commit-messages`, `error-handling`, `docstring-style`) never needed the preload fix above — they were already correctly configured — so nobody reran them when the fix went in, and their own "before" data point has only 6 skills in context while the "after" one has all 25. Compliance on those six moved from 88.2% (15/17) down to 76.5% (13/17) across that unplanned change, plausibly a context-dilution effect (more unrelated skills competing for the same output), but this is a confound observed once, not a controlled test.
4. **A third scoring bug, found comparing the two 19-skill samples.** `score_mutation_evals.py` applied one global iteration number to every workspace, silently dropping 16 of 31 mutation trials and reporting an inflated `MutationScore` of 20% instead of the true 9.7%. Fixed; the corrected number is below.

Full narrative — including all three mutation kills and a finding that contradicts the original hand-built pilot — is in `docs/results.md` Part 5.

## Headline numbers (second sample, the most complete valid measurement)

| Metric | Value |
|---|---|
| Task Suite Coverage | 100% (31/31 evals ran) |
| Retrieval Rate | 100% (skill always read once relevant) |
| Compliance Coverage, 19-skill expansion set | 76.2% (16/21) — up from 33.3% (7/21) one day earlier, same config |
| Compliance Coverage, whole 25-skill suite (blended with the confounded 6-skill group) | 76.3% (29/38) |
| Mutation Score, whole 25-skill suite | 9.7% (3/31) — first clean measurement |
| Conflict Resolution Rate | 100% (2/2 instantiated tab/space conflicts resolved consistently) |

## The core finding, corrected: alignment is stable, fighting a default is not

Across both valid samples of the 19-skill expansion set:

- **Aligns with a pretrained default → passes, every time, both samples, zero exceptions**: f-strings, no mutable default args, trailing commas, docstring quote style, no semicolons, module-level constant casing.
- **Fights a pretrained default → unstable, not "overridden."** All 10 fight-predicted instructions failed in the first sample — camelCase variable names, `+`-concatenation over f-strings, banned `is_`/`has_`/`should_` boolean prefixes, a 60-character line limit, and others, each instructing the model directly and each one failing. In the second sample, only 3 (currency format, date format, test-function naming) failed cleanly; one (camelCase variable naming) split across its two branches; the other 6 — including the 60-char line limit, boolean naming, passive voice, and measurement units — passed outright. **Our first description of this as "the model overrides fought instructions" held for the first sample and not the second — it isn't a stable property of the model, it's specifically that the fight-predicted side is noisy.**
- **The three "uncertain" skills split exactly as their label predicted**: `trailing-comma` passed both times (turned out to align), `error-period` failed both times (turned out to fight), `quote-style` flipped from Fail to Pass — a coin flip.

## Known weak spots

- **Mutation Score.** 9.7% (3/31) is the first clean, uncontaminated full-suite measurement — the two earlier readings (5% / 1-of-20, then an inflated 20% / 3-of-15) were each invalidated by one of the two bugs above, not by anything about the model. Two of the three kills (`fstring-required`, `string-concat`) come from cross-skill interference — deleting one skill's rule let a *different*, still-loaded skill's conflicting rule fill the gap — not from the model reverting to an unguided default. `docs/results.md` Part 5 has the full account, including two mutation-kill verdicts (`indent-spaces`, `text-styling`'s red branch) that reversed relative to the original hand-built pilot's own baseline.
- `text-styling` (`t_blue`/`t_red`) previously looked broken due to an unrelated cause: a subagent describing a tool call in its final answer without the call actually finishing. The same failure shape recurred on unrelated tasks (`t_constant_naming`, `t_code_mixed`) in the second sample — a general trait of the subagent configuration under slower, multi-step tasks, not something specific to any one skill's domain.
- `commit-messages` needed concrete mock diffs in the prompt to score meaningfully.

## Caveats

- Single run per eval — pilot scale, not statistically powered. The 43-point swing above, on a genuinely identical config, is the direct, measured proof of that, not just a disclaimer.
- ~18% of instruction-branches are LLM-judged (no deterministic checker), not mechanically verified.
- The 6-skill context-dilution finding is one sample under an unplanned config change, not a controlled experiment — treat the direction as a hint worth testing properly, not a settled result.
