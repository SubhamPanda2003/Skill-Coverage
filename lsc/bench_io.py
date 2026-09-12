"""Shared I/O helpers for both the hand-authored pilot and the real-subagent
benchmark path, so task definitions have exactly one source of truth."""
import json

SKILL_DIRS = {
    "text-styling": ".claude/skills/text-styling/SKILL.md",
    "indent-tabs": ".claude/skills/indent-tabs/SKILL.md",
    "indent-spaces": ".claude/skills/indent-spaces/SKILL.md",
    "commit-messages": ".claude/skills/commit-messages/SKILL.md",
    "error-handling": ".claude/skills/error-handling/SKILL.md",
    "docstring-style": ".claude/skills/docstring-style/SKILL.md",
}


def load_tasks(path="benchmark/tasks.json"):
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    for t in raw:
        t["expects"] = [tuple(k) for k in t["expects"]]
    return raw


def parse_key(key_str):
    """'commit-messages#u0#b0' -> ('commit-messages', 0, 0)"""
    skill, u, b = key_str.split("#")
    return (skill, int(u[1:]), int(b[1:]))


def load_real_trajectories(tasks, trajectory_dir="results/trajectories"):
    """Reads results/trajectories/<task_id>.json, each {"artifact": str,
    "judged_verdicts": {"skill#uN#bN": "Pass"|"Fail"}} (judged_verdicts optional)."""
    trajectories = {}
    for t in tasks:
        path = f"{trajectory_dir}/{t['id']}.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        judged = {parse_key(k): v for k, v in data.get("judged_verdicts", {}).items()}
        trajectories[t["id"]] = {"artifact": data["artifact"], "judged_verdicts": judged}
    return trajectories
