"""Scores mutation-adequacy trials under the current agentskills.io-shaped
layout: for every eval, reads any mutant_<key>/outputs/response.md siblings
of its with_skill/ run, compares each against the original verdict, and folds
MutationScore/MutationTrials into results/iteration-N/benchmark.json as
additive keys (not a separate file, unlike the legacy score_mutations.py).

Fork of score_mutations.py, not an edit in place -- the original keeps
scoring the frozen legacy results/mutants/ layout so docs/results.md stays
reproducible. Reuses lsc/oracle.py's evaluate()/is_verifiable() unchanged.
"""
import glob
import json
import os
from lsc import oracle, bench_io


def main():
    tasks = bench_io.load_evals()
    tasks_by_id = {t["id"]: t for t in tasks}
    all_workspaces = {tid: bench_io.workspace_for_task(tid, tasks_by_id) for tid in tasks_by_id}
    iteration = max(bench_io.latest_iteration(ws) for ws in set(all_workspaces.values()))

    root_path = f"results/iteration-{iteration}/benchmark.json"
    if not os.path.exists(root_path):
        raise SystemExit(f"{root_path} not found -- run score_evals.py first.")
    with open(root_path, encoding="utf-8") as f:
        root_bench = json.load(f)

    results = []
    for tid, ws in all_workspaces.items():
        # Each task's own with_skill run lives under its own workspace's
        # latest iteration, which need not equal the global max computed
        # above -- workspaces grow independently, so a task whose workspace
        # is behind the max would silently glob an iteration-N directory
        # that doesn't exist yet, finding zero mutants and never erroring.
        task_iteration = bench_io.latest_iteration(ws)
        eval_dir = f"{ws}/iteration-{task_iteration}/eval-{tid}"
        for mdir in sorted(glob.glob(f"{eval_dir}/mutant_*")):
            key = os.path.basename(mdir)[len("mutant_"):]
            skill, u, b = bench_io.parse_key(key)
            with open(f"{mdir}/outputs/response.md", encoding="utf-8") as f:
                mutant_artifact = f.read()
            original_verdict = root_bench["per_task"].get(tid, {}).get(key)
            mutant_verdict = oracle.evaluate(skill, u, b, mutant_artifact)
            killed = original_verdict == "Pass" and mutant_verdict == "Fail"
            results.append({"key": key, "task_id": tid, "original_verdict": original_verdict,
                             "mutant_verdict": mutant_verdict, "killed": killed})

    n = len(results)
    killed_n = sum(1 for r in results if r["killed"])
    root_bench["mutation_trials"] = results
    root_bench["MutationTrials"] = n
    root_bench["MutationScore"] = (killed_n / n) if n else None

    with open(root_path, "w", encoding="utf-8") as f:
        json.dump(root_bench, f, indent=2, default=str)

    print(json.dumps({"MutationTrials": n, "MutationScore": root_bench["MutationScore"], "trials": results}, indent=2))
    print(f"\nFolded mutation results into {root_path}")


if __name__ == "__main__":
    main()
