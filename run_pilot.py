"""Layered Skill Coverage -- pilot validation run.

IMPORTANT SCOPE NOTE: no live LLM agent was available to script in this
environment (no API key configured). The trajectories below are hand-authored
by the pipeline author to exercise every path the pipeline needs to
distinguish (pass / fail / unretrieved / conflicting-skills / mutation-killed
/ mutation-survived) with known ground truth -- the same way you would
unit-test a coverage tool before trusting it on real, expensive, uncontrolled
agent runs. These are NOT live multi-model results and must not be reported
as such.
"""
import json
from lsc import core, analysis, report, bench_io

SKILL_DIRS = bench_io.SKILL_DIRS
TASKS = bench_io.load_tasks()

TRAJECTORIES = {
    "t_blue": {"artifact": "h1 {\n  color: blue;\n  font-size: 20px;\n}\n"},
    "t_red": {"artifact": "h1 {\n  color: red;\n  font-size: 30px;\n}\n"},
    "t_red_unretrieved": {"artifact": "h1 {\n  color: red;\n}\n"},
    "t_code_consistent": {"artifact": "def greet(name):\n\treturn f\"Hello, {name}\"\n"},
    "t_code_mixed": {"artifact": "def greet(name):\n\treturn helper(name)\n\ndef helper(name):\n  return f\"Hello, {name}\"\n"},
    "t_commit_good": {"artifact": "Fix bug in login flow\n",
                       "judged_verdicts": {("commit-messages", 0, 0): "Pass"}},
    "t_commit_bad": {"artifact": "Fixed the bug where login was broken due to token expiry issues\n",
                      "judged_verdicts": {("commit-messages", 0, 0): "Fail"}},
}

MUTATION_TRIALS = [
    {"key": ("text-styling", 0, 1), "task_id": "t_red",
     "mutant_artifact": "h1 {\n  color: red;\n}\n",
     "note": "red/30px instruction deleted from skill -> agent no longer sets font-size"},
    {"key": ("indent-tabs", 1, 0), "task_id": "t_code_consistent",
     "mutant_artifact": "def greet(name):\n\treturn f\"Hello, {name}\"\n",
     "note": "trailing-newline instruction deleted -> artifact unchanged (tool/editor default already does this)"},
]


def main():
    skills = core.load_skills(SKILL_DIRS)
    tasks_by_id = {t["id"]: t for t in TASKS}

    per_key, funnel_metrics, per_task = analysis.run_funnel(skills, TASKS, TRAJECTORIES)
    conflict_pairs = analysis.detect_conflicts(skills)
    conflict_results, conflict_metrics = analysis.conflict_coverage(conflict_pairs, TASKS, TRAJECTORIES)
    mutation_results, mutation_metrics = analysis.mutation_adequacy(MUTATION_TRIALS, tasks_by_id, TRAJECTORIES)

    report_dict = {
        "per_key": {f"{k[0]}#u{k[1]}#b{k[2]}": v for k, v in per_key.items()},
        "per_task": per_task,
        "funnel_metrics": funnel_metrics,
        "conflict_pairs_detected": [{"a": p["a"], "b": p["b"], "a_text": p["a_text"], "b_text": p["b_text"]} for p in conflict_pairs],
        "conflict_results": [{"pair": {"a": r["pair"]["a"], "b": r["pair"]["b"]},
                               "instantiated_tasks": r["instantiated_tasks"],
                               "resolution_verdicts": r["resolution_verdicts"]} for r in conflict_results],
        "conflict_metrics": conflict_metrics,
        "mutation_results": [{"key": r["key"], "task_id": r["task_id"], "original_verdict": r["original_verdict"],
                               "mutant_verdict": r["mutant_verdict"], "killed": r["killed"]} for r in mutation_results],
        "mutation_metrics": mutation_metrics,
    }

    import os
    os.makedirs("results", exist_ok=True)
    with open("results/results.json", "w", encoding="utf-8") as f:
        json.dump(report_dict, f, indent=2, default=str)

    html_report = report.render(skills, per_key, funnel_metrics, conflict_pairs,
                                 conflict_metrics, mutation_metrics, per_task)
    with open("results/report.html", "w", encoding="utf-8") as f:
        f.write(html_report)

    print(json.dumps(report_dict, indent=2, default=str))


if __name__ == "__main__":
    main()
