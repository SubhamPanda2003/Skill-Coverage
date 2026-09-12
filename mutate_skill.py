"""Applies or restores a single-unit-deletion mutant on a real .claude/skills
SKILL.md file, so a real subagent can be rerun against the mutated skill.

Usage:
  python3 mutate_skill.py apply <skill_name> <unit_index>
  python3 mutate_skill.py restore <skill_name>

`apply` backs up the original file to SKILL.md.orig before overwriting it.
`restore` must always be called after `apply`, even if the subsequent
subagent call fails -- it puts the original content back and removes the
backup. Never leave a skill file mutated between command invocations.
"""
import sys
from lsc import core, bench_io


def apply(skill_name, unit_index):
    path = bench_io.SKILL_DIRS[skill_name]
    backup_path = path + ".orig"
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(raw)

    fm, body = core.parse_skill_md(raw)
    units = core.segment(skill_name, body)
    unit = units[unit_index]
    mutant_body = body[:unit.start] + body[unit.end:]
    fm_text = "\n".join(f"{k}: {v}" for k, v in fm.items())
    mutant_raw = f"---\n{fm_text}\n---\n{mutant_body}"

    with open(path, "w", encoding="utf-8") as f:
        f.write(mutant_raw)
    print(f"Mutated {path}: removed unit[{unit_index}] = {unit.text!r}")


def restore(skill_name):
    path = bench_io.SKILL_DIRS[skill_name]
    backup_path = path + ".orig"
    with open(backup_path, "r", encoding="utf-8") as f:
        raw = f.read()
    with open(path, "w", encoding="utf-8") as f:
        f.write(raw)
    import os
    os.remove(backup_path)
    print(f"Restored {path} from backup.")


if __name__ == "__main__":
    if sys.argv[1] == "apply":
        apply(sys.argv[2], int(sys.argv[3]))
    elif sys.argv[1] == "restore":
        restore(sys.argv[2])
    else:
        raise SystemExit("usage: mutate_skill.py apply <skill> <unit_index> | restore <skill>")
