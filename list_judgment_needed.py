"""Prints one JSON line per (task, Judged-tier constraint) pair that needs an
LLM judge verdict, per each task's ground-truth `expects` list. Consumed by
the /lsc-run-benchmark command so it doesn't have to re-derive this mapping
by hand."""
import json
from lsc import core, oracle, bench_io


def main():
    skills = core.load_skills(bench_io.SKILL_DIRS)
    tasks = bench_io.load_evals()
    for task in tasks:
        for key in task["expects"]:
            skill, ui, bi = key
            if not oracle.is_verifiable(skill, ui, bi):
                unit = skills[skill]["units"][ui]
                print(json.dumps({
                    "task_id": task["id"],
                    "task_text": task["text"],
                    "key": f"{skill}#u{ui}#b{bi}",
                    "unit_text": unit.text,
                }))


if __name__ == "__main__":
    main()
