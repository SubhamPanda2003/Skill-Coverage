"""Prints one JSON line per (task, Verifiable constraint) pair that originally
scored Pass in the live run -- these are the only pairs mutation-adequacy can
say anything about (a Fail can't be "killed" further). Requires
results/live/results.json from a prior /lsc-run-benchmark + /lsc-score."""
import json
import os
from lsc import bench_io, oracle


def main():
    path = "results/live/results.json"
    if not os.path.exists(path):
        raise SystemExit(f"{path} not found -- run /lsc-run-benchmark then /lsc-score first.")
    with open(path, "r", encoding="utf-8") as f:
        live = json.load(f)

    tasks_by_id = {t["id"]: t for t in bench_io.load_tasks()}
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
