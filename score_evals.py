"""Scores the current agentskills.io-shaped evals/workspace layout (see
docs/results.md's migration note). Reads .claude/skills/*/evals/evals.json +
evals/cross-skill.json and each eval's latest iteration-N/eval-<id>/with_skill/
{outputs/response.md, grading.json}; writes each skill's own scoped
<skill>-workspace/iteration-N/benchmark.json plus the whole-suite rollup at
results/iteration-N/benchmark.json.

This is a fork of score_trajectories.py, not an edit in place -- the original
keeps working against the frozen legacy results/trajectories/ layout so
docs/results.md Parts 1-3 stay reproducible. Reuses lsc/analysis.py's
run_funnel/detect_conflicts/conflict_coverage completely unchanged; only the
I/O boundaries (what feeds them, where output lands) differ.

Requires: every eval in evals.json to have an outputs/response.md + grading.json
under its workspace's latest iteration (run /lsc-run-benchmark first).
"""
import glob
import json
import os
from lsc import core, analysis, oracle, report, bench_io


def refresh_grading(base_dir, expects, artifact, skills):
    """Rewrite this run's grading.json: Verifiable entries are always
    recomputed fresh from outputs/response.md (so an oracle bug fix, like the
    docstring-line-length one, propagates to old iterations with zero new
    subagent calls); Judged entries are preserved from whatever a real
    lsc-judge call already recorded, since a scorer can't produce those
    itself. grading.json is scorer-owned -- this is meant to run every time
    /lsc-score runs, never treated as a write-once capture."""
    grading_path = f"{base_dir}/grading.json"
    existing = {}
    if os.path.exists(grading_path):
        with open(grading_path, encoding="utf-8") as f:
            for a in json.load(f)["assertion_results"]:
                existing[a["lsc_key"]] = a

    assertion_results = []
    for k in expects:
        key_str = f"{k[0]}#u{k[1]}#b{k[2]}"
        text = skills[k[0]]["units"][k[1]].text
        if oracle.is_verifiable(*k):
            passed = oracle.evaluate(*k, artifact) == "Pass"
            evidence = oracle.evidence_for(*k, artifact)
        else:
            old = existing.get(key_str)
            passed = old["passed"] if old else False
            evidence = old["evidence"] if old else "(no judge verdict recorded yet -- run /lsc-run-benchmark's judge step)"
        assertion_results.append({"text": text, "lsc_key": key_str, "passed": passed, "evidence": evidence})

    passed_n = sum(1 for a in assertion_results if a["passed"])
    grading = {
        "assertion_results": assertion_results,
        "summary": {
            "passed": passed_n, "failed": len(assertion_results) - passed_n,
            "total": len(assertion_results),
            "pass_rate": (passed_n / len(assertion_results)) if assertion_results else None,
        },
    }
    with open(grading_path, "w", encoding="utf-8") as f:
        json.dump(grading, f, indent=2)


def pass_rate_summary(eval_ids, workspace_of):
    rates = []
    for tid in eval_ids:
        ws = workspace_of if isinstance(workspace_of, str) else workspace_of[tid]
        it = bench_io.latest_iteration(ws)
        with open(f"{ws}/iteration-{it}/eval-{tid}/with_skill/grading.json", encoding="utf-8") as f:
            g = json.load(f)
        if g["summary"]["pass_rate"] is not None:
            rates.append(g["summary"]["pass_rate"])
    if not rates:
        return None
    mean = sum(rates) / len(rates)
    stddev = (sum((r - mean) ** 2 for r in rates) / len(rates)) ** 0.5 if len(rates) > 1 else 0.0
    return {"mean": mean, "stddev": stddev}


def main():
    skills = core.load_skills(bench_io.SKILL_DIRS)
    tasks = bench_io.load_evals()
    tasks_by_id = {t["id"]: t for t in tasks}

    all_workspaces = {tid: bench_io.workspace_for_task(tid, tasks_by_id) for tid in tasks_by_id}
    missing = []
    for tid, ws in all_workspaces.items():
        it = bench_io.latest_iteration(ws)
        if not os.path.exists(f"{ws}/iteration-{it}/eval-{tid}/with_skill/outputs/response.md"):
            missing.append(tid)
    if missing:
        raise SystemExit(f"Missing eval runs for {missing} -- run /lsc-run-benchmark first.")

    # Always refresh grading.json from the actual outputs/response.md before
    # scoring anything -- Verifiable verdicts/evidence are fully recomputed
    # here (see refresh_grading's docstring), so a fixed oracle check
    # propagates to every run, not just future ones.
    for tid, ws in all_workspaces.items():
        it = bench_io.latest_iteration(ws)
        eval_dir = f"{ws}/iteration-{it}/eval-{tid}"
        expects = tasks_by_id[tid]["expects"]
        with open(f"{eval_dir}/with_skill/outputs/response.md", encoding="utf-8") as f:
            artifact = f.read()
        refresh_grading(f"{eval_dir}/with_skill", expects, artifact, skills)
        for mdir in sorted(glob.glob(f"{eval_dir}/mutant_*")):
            key = os.path.basename(mdir)[len("mutant_"):]
            k = bench_io.parse_key(key)
            with open(f"{mdir}/outputs/response.md", encoding="utf-8") as f:
                mutant_artifact = f.read()
            refresh_grading(mdir, [k], mutant_artifact, skills)

    trajectories = bench_io.load_evals_trajectories(tasks)
    iteration = max(bench_io.latest_iteration(ws) for ws in set(all_workspaces.values()))

    # Per-skill scoped benchmark.json (real numbers, not stubs -- see docs/results.md)
    for skill_name in bench_io.SKILL_DIRS:
        subset = {skill_name: skills[skill_name]}
        per_key, funnel_metrics, per_task = analysis.run_funnel(subset, tasks, trajectories)
        per_task_nonempty = {tid: v for tid, v in per_task.items() if v}
        eval_ids = list(per_task_nonempty.keys())
        ws = f".claude/skills/{skill_name}-workspace"
        bench = {
            "run_summary": {
                "with_skill": {"pass_rate": pass_rate_summary(
                    eval_ids, {tid: all_workspaces[tid] for tid in eval_ids}) if eval_ids else None},
                "without_skill": None,
                "delta": None,
            },
            "lsc_funnel_metrics": funnel_metrics,
            "lsc_per_key": {f"{k[0]}#u{k[1]}#b{k[2]}": v for k, v in per_key.items()},
            "lsc_per_task": per_task_nonempty,
        }
        it = bench_io.latest_iteration(ws) or iteration
        os.makedirs(f"{ws}/iteration-{it}", exist_ok=True)
        with open(f"{ws}/iteration-{it}/benchmark.json", "w", encoding="utf-8") as f:
            json.dump(bench, f, indent=2)

    # Whole-suite rollup
    per_key, funnel_metrics, per_task = analysis.run_funnel(skills, tasks, trajectories)
    conflict_pairs = analysis.detect_conflicts(skills)
    conflict_results, conflict_metrics = analysis.conflict_coverage(conflict_pairs, tasks, trajectories)
    all_eval_ids = [t["id"] for t in tasks]

    root_bench = {
        "run_summary": {
            "with_skill": {"pass_rate": pass_rate_summary(all_eval_ids, all_workspaces)},
            "without_skill": None,
            "delta": None,
        },
        "TaskSuiteCoverage": funnel_metrics["TaskSuiteCoverage"],
        "RetrievalRate": funnel_metrics["RetrievalRate"],
        "ComplianceCoverage": funnel_metrics["ComplianceCoverage"],
        "VerifiableCoverage": funnel_metrics["VerifiableCoverage"],
        "Verifiable_n": funnel_metrics["Verifiable_n"],
        "JudgedCoverage": funnel_metrics["JudgedCoverage"],
        "Judged_n": funnel_metrics["Judged_n"],
        "ConflictPairsDetected": conflict_metrics["ConflictPairsDetected"],
        "ConflictInstantiatedRate": conflict_metrics["ConflictInstantiatedRate"],
        "ConflictResolutionRate": conflict_metrics["ConflictResolutionRate"],
        "ConflictResolutionInstances": conflict_metrics["ConflictResolutionInstances"],
        "per_key": {f"{k[0]}#u{k[1]}#b{k[2]}": v for k, v in per_key.items()},
        "per_task": per_task,
        "conflict_pairs_detected": [{"a": p["a"], "b": p["b"], "a_text": p["a_text"], "b_text": p["b_text"]} for p in conflict_pairs],
        "conflict_results": [{"pair": {"a": r["pair"]["a"], "b": r["pair"]["b"]},
                               "instantiated_tasks": r["instantiated_tasks"],
                               "resolution_verdicts": r["resolution_verdicts"]} for r in conflict_results],
    }
    os.makedirs(f"results/iteration-{iteration}", exist_ok=True)
    with open(f"results/iteration-{iteration}/benchmark.json", "w", encoding="utf-8") as f:
        json.dump(root_bench, f, indent=2, default=str)

    html_report = report.render(skills, per_key, funnel_metrics, conflict_pairs,
                                 conflict_metrics, {"MutationTrials": 0, "MutationScore": None}, per_task)
    with open(f"results/iteration-{iteration}/report.html", "w", encoding="utf-8") as f:
        f.write(html_report)

    print(json.dumps(root_bench, indent=2, default=str))
    print(f"\nWrote results/iteration-{iteration}/benchmark.json + report.html, "
          f"plus each skill's own <skill>-workspace/iteration-N/benchmark.json.")


if __name__ == "__main__":
    main()
