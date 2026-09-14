"""Shared I/O helpers for the live benchmark: loading eval definitions and
their scored run artifacts from the agentskills.io-shaped layout."""
import glob
import json
import os

from . import oracle

SKILL_DIRS = {
    "text-styling": ".claude/skills/text-styling/SKILL.md",
    "indent-tabs": ".claude/skills/indent-tabs/SKILL.md",
    "indent-spaces": ".claude/skills/indent-spaces/SKILL.md",
    "commit-messages": ".claude/skills/commit-messages/SKILL.md",
    "error-handling": ".claude/skills/error-handling/SKILL.md",
    "docstring-style": ".claude/skills/docstring-style/SKILL.md",
    # Added for the 25-skill expansion (docs/results.md Part 5): each one
    # designed to predict whether its instruction fights or aligns with a
    # plausible pretrained default, per the paper's own flagged next step.
    "date-format": ".claude/skills/date-format/SKILL.md",
    "quote-style": ".claude/skills/quote-style/SKILL.md",
    "variable-naming": ".claude/skills/variable-naming/SKILL.md",
    "line-length-limit": ".claude/skills/line-length-limit/SKILL.md",
    "currency-format": ".claude/skills/currency-format/SKILL.md",
    "boolean-naming": ".claude/skills/boolean-naming/SKILL.md",
    "measurement-units": ".claude/skills/measurement-units/SKILL.md",
    "string-concat": ".claude/skills/string-concat/SKILL.md",
    "test-naming": ".claude/skills/test-naming/SKILL.md",
    "em-dash-ban": ".claude/skills/em-dash-ban/SKILL.md",
    "passive-voice": ".claude/skills/passive-voice/SKILL.md",
    "docstring-quotes": ".claude/skills/docstring-quotes/SKILL.md",
    "constant-naming": ".claude/skills/constant-naming/SKILL.md",
    "mutable-default-ban": ".claude/skills/mutable-default-ban/SKILL.md",
    "fstring-required": ".claude/skills/fstring-required/SKILL.md",
    "oxford-comma": ".claude/skills/oxford-comma/SKILL.md",
    "trailing-comma": ".claude/skills/trailing-comma/SKILL.md",
    "error-period": ".claude/skills/error-period/SKILL.md",
    "semicolon-ban": ".claude/skills/semicolon-ban/SKILL.md",
}


def parse_key(key_str):
    """'commit-messages#u0#b0' -> ('commit-messages', 0, 0)"""
    skill, u, b = key_str.split("#")
    return (skill, int(u[1:]), int(b[1:]))


def load_evals():
    """Loads every task from the per-skill evals/evals.json files plus the
    root evals/cross-skill.json sidecar (for evals that deliberately target
    2+ skills), translating field names to the shape run_funnel() expects:
    {"id","text","expects":[(skill,unit_idx,branch_idx),...]}."""
    tasks = []
    for path in sorted(glob.glob(".claude/skills/*/evals/evals.json")):
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        for e in obj["evals"]:
            tasks.append({
                "id": e["id"], "text": e["prompt"],
                "expects": [tuple(k) for k in e["lsc_targets"]],
            })
    cross_path = "evals/cross-skill.json"
    if os.path.exists(cross_path):
        with open(cross_path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        for e in obj["evals"]:
            tasks.append({
                "id": e["id"], "text": e["prompt"],
                "expects": [tuple(k) for k in e["lsc_targets"]],
            })
    return tasks


def workspace_for_task(task_id, tasks_by_id=None):
    """<skill>-workspace for a single-skill eval, cross-skill-workspace for
    one that targets 2+ skills. tasks_by_id: {id: {"expects":[(skill,u,b)]}}
    -- pass the dict from load_evals() indexed by id; loads it itself if omitted."""
    if tasks_by_id is None:
        tasks_by_id = {t["id"]: t for t in load_evals()}
    skill_names = sorted({k[0] for k in tasks_by_id[task_id]["expects"]})
    if len(skill_names) == 1:
        return f".claude/skills/{skill_names[0]}-workspace"
    return "cross-skill-workspace"


def latest_iteration(workspace_dir):
    """Highest existing iteration-N under workspace_dir, or 0 if none exist yet."""
    if not os.path.isdir(workspace_dir):
        return 0
    nums = []
    for name in os.listdir(workspace_dir):
        if name.startswith("iteration-"):
            try:
                nums.append(int(name[len("iteration-"):]))
            except ValueError:
                pass
    return max(nums, default=0)


def load_evals_trajectories(tasks, iteration=None):
    """Reads <workspace>/iteration-N/eval-<id>/with_skill/{outputs/response.md,
    grading.json} for every task, returning {task_id: {"artifact","judged_verdicts"}}.
    judged_verdicts here means "every Judged-tier verdict grading.json already
    recorded", re-derived fresh each call -- grading.json is scorer-owned and
    always regeneratable from outputs/response.md, never a frozen capture, so
    a future oracle fix (like the docstring-line-length one) still propagates
    to old iterations without any new subagent calls."""
    tasks_by_id = {t["id"]: t for t in tasks}
    trajectories = {}
    for t in tasks:
        ws = workspace_for_task(t["id"], tasks_by_id)
        it = iteration or latest_iteration(ws)
        base = f"{ws}/iteration-{it}/eval-{t['id']}/with_skill"
        with open(f"{base}/outputs/response.md", "r", encoding="utf-8") as f:
            artifact = f.read()
        judged = {}
        grading_path = f"{base}/grading.json"
        if os.path.exists(grading_path):
            with open(grading_path, "r", encoding="utf-8") as f:
                grading = json.load(f)
            for a in grading["assertion_results"]:
                key = parse_key(a["lsc_key"])
                if not oracle.is_verifiable(*key):
                    judged[key] = "Pass" if a["passed"] else "Fail"
        trajectories[t["id"]] = {"artifact": artifact, "judged_verdicts": judged}
    return trajectories
