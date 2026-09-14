"""Prints one JSON line per (task, Verifiable constraint) pair that originally
scored Pass in the live run -- these are the only pairs mutation-adequacy can
say anything about (a Fail can't be "killed" further). Requires
results/iteration-N/benchmark.json from a prior /lsc-run-benchmark + /lsc-score."""
import json
import os
from lsc import bench_io, oracle


def main():
    tasks = bench_io.load_evals()
    tasks_by_id = {t["id"]: t for t in tasks}
    all_workspaces = {tid: bench_io.workspace_for_task(tid, tasks_by_id) for tid in tasks_by_id}
    iteration = max(bench_io.latest_iteration(ws) for ws in set(all_workspaces.values()))
    path = f"results/iteration-{iteration}/benchmark.json"
    if not os.path.exists(path):
        raise SystemExit(f"{path} not found -- run /lsc-run-benchmark then /lsc-score first.")
    with open(path, "r", encoding="utf-8") as f:
        live = json.load(f)
    for task_id, keys in live["per_task"].items():
        for key, verdict in keys.items():
            if verdict != "Pass":
                continue
            skill, u, b = bench_io.parse_key(key)
            if not oracle.is_verifiable(skill, u, b):
                continue  # mutation-adequacy is scoped to the deterministic subset
            print(json.dumps({
                "task_id": task_id, "task_text": tasks_by_id[task_id]["text"],
                "key": key, "skill": skill, "unit_index": u,
            }))


if __name__ == "__main__":
    main()
