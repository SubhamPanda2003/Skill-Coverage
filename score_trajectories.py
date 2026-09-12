"""Scores REAL trajectories collected by the /lsc-run-benchmark command
(results/trajectories/<task_id>.json, one per task, written by real Claude
Code subagents). Mirrors run_pilot.py's pipeline exactly, but reads live
agent output instead of hand-authored fixtures -- this is the script that
produces an actual empirical result, not a pipeline-validation one.

Requires: results/trajectories/<task_id>.json to exist for every task in
benchmark/tasks.json (run /lsc-run-benchmark first).
"""
import json
import os
from lsc import core, analysis, report, bench_io


def main():
    skills = core.load_skills(bench_io.SKILL_DIRS)
    tasks = bench_io.load_tasks()

    missing = [t["id"] for t in tasks if not os.path.exists(f"results/trajectories/{t['id']}.json")]
    if missing:
        raise SystemExit(f"Missing trajectories for tasks {missing} -- run /lsc-run-benchmark first.")

    trajectories = bench_io.load_real_trajectories(tasks)

    per_key, funnel_metrics, per_task = analysis.run_funnel(skills, tasks, trajectories)
    conflict_pairs = analysis.detect_conflicts(skills)
    conflict_results, conflict_metrics = analysis.conflict_coverage(conflict_pairs, tasks, trajectories)

    report_dict = {
        "source": "live-subagent-trajectories",
        "per_key": {f"{k[0]}#u{k[1]}#b{k[2]}": v for k, v in per_key.items()},
        "per_task": per_task,
        "funnel_metrics": funnel_metrics,
        "conflict_pairs_detected": [{"a": p["a"], "b": p["b"], "a_text": p["a_text"], "b_text": p["b_text"]} for p in conflict_pairs],
        "conflict_results": [{"pair": {"a": r["pair"]["a"], "b": r["pair"]["b"]},
                               "instantiated_tasks": r["instantiated_tasks"],
                               "resolution_verdicts": r["resolution_verdicts"]} for r in conflict_results],
        "conflict_metrics": conflict_metrics,
        "note": "No mutation-adequacy pass included yet -- that needs a second round of "
                "subagent runs against mutated skill files, not yet wired into these commands.",
    }

    os.makedirs("results/live", exist_ok=True)
    with open("results/live/results.json", "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2, default=str)

    html_report = report.render(skills, per_key, funnel_metrics, conflict_pairs,
                                 conflict_metrics, {"MutationTrials": 0, "MutationScore": None}, per_task)
    with open("results/live/report.html", "w", encoding="utf-8") as f:
        f.write(html_report)

    print(json.dumps(report_dict, indent=2, default=str))
    print("\nWrote results/live/results.json and results/live/report.html")


if __name__ == "__main__":
    main()
