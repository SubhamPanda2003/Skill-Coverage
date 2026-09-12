"""Scores mutant artifacts collected by /lsc-mutate (results/mutants/<key>__<task_id>.json,
each {"artifact": str}) against the original live verdict, and writes
results/mutation/results.json with the mutation-adequacy score."""
import json
import os
from lsc import oracle, bench_io


def _live_candidates(live):
    """(task_id, key) pairs that originally scored Pass on a Verifiable unit --
    the same set list_mutation_candidates.py prints. Anything else found in
    results/mutants/ is a stale file from a different live/results.json and
    must not be scored against this one."""
    out = set()
    for task_id, keys in live["per_task"].items():
        for key, verdict in keys.items():
            if verdict != "Pass":
                continue
            skill, u, b = bench_io.parse_key(key)
            if not oracle.is_verifiable(skill, u, b):
                continue
            out.add((task_id, key))
    return out


def main():
    with open("results/live/results.json", "r", encoding="utf-8") as f:
        live = json.load(f)

    mutant_dir = "results/mutants"
    if not os.path.isdir(mutant_dir) or not os.listdir(mutant_dir):
        raise SystemExit(f"No mutant artifacts found in {mutant_dir} -- run /lsc-mutate first.")

    candidates = _live_candidates(live)
    seen = set()
    results = []
    for fname in sorted(os.listdir(mutant_dir)):
        if not fname.endswith(".json"):
            continue
        key, task_id = fname[:-5].split("__")
        if (task_id, key) not in candidates:
            print(f"Skipping {fname}: not a mutation candidate for the current "
                  f"results/live/results.json (stale file from a different run?)")
            continue
        seen.add((task_id, key))
        with open(f"{mutant_dir}/{fname}", "r", encoding="utf-8") as f:
            mutant_artifact = json.load(f)["artifact"]
        skill, u, b = bench_io.parse_key(key)
        original_verdict = live["per_task"][task_id][key]
        mutant_verdict = oracle.evaluate(skill, u, b, mutant_artifact)
        killed = original_verdict == "Pass" and mutant_verdict == "Fail"
        results.append({"key": key, "task_id": task_id, "original_verdict": original_verdict,
                         "mutant_verdict": mutant_verdict, "killed": killed})

    for task_id, key in sorted(candidates - seen):
        print(f"Warning: no mutant artifact for candidate {key}__{task_id} -- run /lsc-mutate for it.")

    n = len(results)
    killed = sum(1 for r in results if r["killed"])
    out = {"source": "live-subagent-mutation-trials", "trials": results,
           "MutationTrials": n, "MutationScore": (killed / n) if n else None}

    os.makedirs("results/mutation", exist_ok=True)
    with open("results/mutation/results.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
