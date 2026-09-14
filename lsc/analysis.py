"""Coverage funnel, cross-skill conflict detection, and mutation-adequacy scoring."""
from . import core, oracle


def all_branch_keys(skills):
    """Every (skill, unit_index, branch_index) triple in the loaded skill set."""
    keys = []
    for skill_name, skill in skills.items():
        for ui, unit in enumerate(skill["units"]):
            for bi, _ in enumerate(unit.branches):
                keys.append((skill_name, ui, bi))
    return keys


def run_funnel(skills, tasks, trajectories):
    """tasks: [{id, text, expects: [(skill,unit_idx,branch_idx), ...]}]
    trajectories: {task_id: {"artifact": str, "judged_verdicts": {key: "Pass"/"Fail"}}}
    Returns per-key status plus the three funnel metrics."""
    keys = all_branch_keys(skills)
    instantiated = {k: False for k in keys}
    retrieved_by = {k: [] for k in keys}   # task ids where Exposed
    verdicts = {k: [] for k in keys}       # list of "Pass"/"Fail" across exposed tasks

    per_task = {}
    for task in tasks:
        activated = core.discover(task["text"], skills)
        traj = trajectories[task["id"]]
        per_task[task["id"]] = {}
        for key in task["expects"]:
            skill_name = key[0]
            if key not in instantiated:
                continue  # key's skill isn't in this call's `skills` subset
            instantiated[key] = True
            if skill_name in activated:
                verdict = oracle.evaluate(*key, traj["artifact"], traj.get("judged_verdicts"))
                retrieved_by[key].append(task["id"])
                verdicts[key].append(verdict)
                per_task[task["id"]][f"{key[0]}#u{key[1]}#b{key[2]}"] = verdict
            else:
                per_task[task["id"]][f"{key[0]}#u{key[1]}#b{key[2]}"] = "Unretrieved"

    def status(k):
        if not instantiated[k]:
            return "Untested"
        if not retrieved_by[k]:
            return "Unretrieved"
        return "Pass" if "Pass" in verdicts[k] else "Fail"

    per_key = {k: {"status": status(k), "verdicts": verdicts[k], "verified": oracle.is_verifiable(*k)} for k in keys}

    n = len(keys)
    n_inst = sum(instantiated.values())
    n_exposed = sum(1 for k in keys if retrieved_by[k])
    n_pass = sum(1 for k in keys if retrieved_by[k] and "Pass" in verdicts[k])

    metrics = {
        "TaskSuiteCoverage": n_inst / n if n else 0.0,
        "RetrievalRate": (n_exposed / n_inst) if n_inst else 0.0,
        "ComplianceCoverage": (n_pass / n_exposed) if n_exposed else 0.0,
    }
    for tier in ("Verifiable", "Judged"):
        tier_keys = [k for k in keys if instantiated[k] and (oracle.is_verifiable(*k) == (tier == "Verifiable"))]
        tier_exposed = [k for k in tier_keys if retrieved_by[k]]
        tier_pass = [k for k in tier_exposed if "Pass" in verdicts[k]]
        metrics[f"{tier}Coverage"] = (len(tier_pass) / len(tier_exposed)) if tier_exposed else None
        metrics[f"{tier}_n"] = len(tier_keys)
    return per_key, metrics, per_task


def topic_keywords(unit):
    stripped = core.CHECKABLE_TOKEN.sub(" ", unit.text)
    return core.tokenize(stripped)


def detect_conflicts(skills):
    """Heuristic cross-skill conflict detector: two Verifiable, unconditional units
    from *different* skills conflict if their topical keywords overlap but the
    concrete checkable tokens they assert are disjoint (e.g. 'tabs' vs 'spaces').
    This is validated here against one known case, not a general semantic detector."""
    candidates = []
    for skill_name, skill in skills.items():
        for ui, unit in enumerate(skill["units"]):
            if unit.type == "Verifiable" and len(unit.branches) == 1 and unit.branches[0].cond_text == "(unconditional)":
                candidates.append((skill_name, ui, unit))

    pairs = []
    for i in range(len(candidates)):
        for j in range(i + 1, len(candidates)):
            a_skill, a_idx, a_unit = candidates[i]
            b_skill, b_idx, b_unit = candidates[j]
            if a_skill == b_skill:
                continue
            if not core.keyword_overlap(topic_keywords(a_unit), topic_keywords(b_unit)):
                continue
            a_val = {m.group(0).lower() for m in core.CHECKABLE_TOKEN.finditer(a_unit.text)}
            b_val = {m.group(0).lower() for m in core.CHECKABLE_TOKEN.finditer(b_unit.text)}
            if a_val and b_val and a_val.isdisjoint(b_val):
                pairs.append({
                    "a": (a_skill, a_idx, 0), "b": (b_skill, b_idx, 0),
                    "a_text": a_unit.text, "b_text": b_unit.text,
                })
    return pairs


def conflict_coverage(conflict_pairs, tasks, trajectories):
    results = []
    for pair in conflict_pairs:
        instantiated_tasks = [t for t in tasks if pair["a"] in t["expects"] and pair["b"] in t["expects"]]
        resolution = []
        for t in instantiated_tasks:
            artifact = trajectories[t["id"]]["artifact"]
            tabs, spaces = oracle.indent_style(artifact)
            resolution.append("Pass" if not (tabs > 0 and spaces > 0) else "Fail")
        results.append({
            "pair": pair, "instantiated_tasks": [t["id"] for t in instantiated_tasks],
            "resolution_verdicts": resolution,
        })
    n_pairs = len(conflict_pairs)
    n_instantiated_pairs = sum(1 for r in results if r["instantiated_tasks"])
    all_verdicts = [v for r in results for v in r["resolution_verdicts"]]
    metrics = {
        "ConflictPairsDetected": n_pairs,
        "ConflictInstantiatedRate": (n_instantiated_pairs / n_pairs) if n_pairs else None,
        "ConflictResolutionRate": (all_verdicts.count("Pass") / len(all_verdicts)) if all_verdicts else None,
        "ConflictResolutionInstances": len(all_verdicts),
    }
    return results, metrics


def mutation_adequacy(mutation_trials, tasks_by_id, trajectories):
    """mutation_trials: [{"key": (skill,unit_idx,branch_idx), "task_id":..., "mutant_artifact": str}]
    Compares the original verdict (from `trajectories`) against the verdict on the
    mutant artifact for the same task/branch."""
    results = []
    for trial in mutation_trials:
        key = trial["key"]
        task = tasks_by_id[trial["task_id"]]
        orig_artifact = trajectories[trial["task_id"]]["artifact"]
        judged = trajectories[trial["task_id"]].get("judged_verdicts")
        v_orig = oracle.evaluate(*key, orig_artifact, judged)
        v_mut = oracle.evaluate(*key, trial["mutant_artifact"], judged)
        killed = v_orig == "Pass" and v_mut == "Fail"
        results.append({"key": key, "task_id": trial["task_id"], "original_verdict": v_orig,
                         "mutant_verdict": v_mut, "killed": killed})
    n = len(results)
    killed = sum(1 for r in results if r["killed"])
    score = (killed / n) if n else None
    return results, {"MutationTrials": n, "MutationScore": score}
