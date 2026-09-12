"""Renders an HTML coverage report: each SKILL.md body shown verbatim with
branch-level gutter highlighting, plus the funnel/conflict/mutation metrics."""
import html

COLORS = {
    "Pass": "#1a7f37", "Fail": "#c53030", "Unretrieved": "#a3a3a3", "Untested": "#e2e2e2",
}
BG = {
    "Pass": "#e6f4ea", "Fail": "#fdecec", "Unretrieved": "#eeeeee", "Untested": "#f5f5f5",
}


def render_skill_html(skill_name, skill, per_key):
    body = skill["body"]
    spans = []
    for ui, unit in enumerate(skill["units"]):
        for bi, br in enumerate(unit.branches):
            key = f"{skill_name}#u{ui}#b{bi}"
            status = per_key.get(key, {}).get("status", "Untested")
            spans.append((br.start, br.end, status, key))
    spans.sort(key=lambda s: s[0])

    out, pos = [], 0
    for start, end, status, key in spans:
        if start > pos:
            out.append(html.escape(body[pos:start]))
        color, bg = COLORS[status], BG[status]
        out.append(
            f'<span title="{html.escape(key)}: {status}" '
            f'style="background:{bg};border-bottom:2px solid {color};">'
            f"{html.escape(body[start:end])}</span>"
        )
        pos = end
    out.append(html.escape(body[pos:]))
    return "".join(out)


def render(skills, per_key, funnel_metrics, conflict_pairs, conflict_metrics, mutation_metrics, per_task):
    per_key_flat = {f"{k[0]}#u{k[1]}#b{k[2]}": v for k, v in per_key.items()}
    parts = ["""<!doctype html><html><head><meta charset="utf-8">
<title>Layered Skill Coverage - Pilot Report</title>
<style>
body{font-family:-apple-system,Segoe UI,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;color:#1a1a1a}
pre{white-space:pre-wrap;background:#fafafa;border:1px solid #ddd;border-radius:6px;padding:1rem}
table{border-collapse:collapse;margin:1rem 0;width:100%}
td,th{border:1px solid #ddd;padding:6px 10px;text-align:left;font-size:0.9rem}
th{background:#f5f5f5}
h2{margin-top:2.5rem;border-bottom:1px solid #ddd;padding-bottom:.3rem}
.note{background:#fff8e1;border:1px solid #f0d98a;border-radius:6px;padding:.75rem 1rem;font-size:.9rem}
</style></head><body>
<h1>Layered Skill Coverage &mdash; Pilot Report</h1>
<div class="note"><b>Scope note:</b> trajectories are hand-constructed to exercise every pipeline path
with known ground truth (no live multi-model agent was run in this environment). Treat this as a
pipeline-validation pilot, not an empirical study of real agent behavior.</div>
"""]

    parts.append("<h2>Funnel metrics</h2><table><tr><th>Metric</th><th>Value</th></tr>")
    for k, v in funnel_metrics.items():
        vv = f"{v:.1%}" if isinstance(v, float) else v
        parts.append(f"<tr><td>{k}</td><td>{vv}</td></tr>")
    parts.append("</table>")

    parts.append("<h2>Cross-skill conflicts detected</h2><table><tr><th>Unit A</th><th>Unit B</th></tr>")
    for p in conflict_pairs:
        parts.append(f"<tr><td>{html.escape(p['a_text'])}</td><td>{html.escape(p['b_text'])}</td></tr>")
    parts.append("</table><table><tr><th>Metric</th><th>Value</th></tr>")
    for k, v in conflict_metrics.items():
        vv = f"{v:.1%}" if isinstance(v, float) else v
        parts.append(f"<tr><td>{k}</td><td>{vv}</td></tr>")
    parts.append("</table>")

    parts.append("<h2>Mutation adequacy</h2><table><tr><th>Metric</th><th>Value</th></tr>")
    for k, v in mutation_metrics.items():
        vv = f"{v:.1%}" if isinstance(v, float) else v
        parts.append(f"<tr><td>{k}</td><td>{vv}</td></tr>")
    parts.append("</table>")

    parts.append("<h2>Skills (verbatim, gutter-highlighted by aggregate status)</h2>")
    legend = "".join(f'<span style="background:{BG[s]};border-bottom:2px solid {COLORS[s]};padding:2px 6px;margin-right:8px">{s}</span>' for s in COLORS)
    parts.append(f"<p>{legend}</p>")
    for name, skill in skills.items():
        parts.append(f"<h3>{html.escape(name)}</h3><pre>{render_skill_html(name, skill, per_key_flat)}</pre>")

    parts.append("<h2>Per-task detail (the aggregate rollup above can mask this)</h2>")
    parts.append("<table><tr><th>Task</th><th>Key</th><th>Verdict</th></tr>")
    for task_id, keys in per_task.items():
        for key, verdict in keys.items():
            parts.append(f"<tr><td>{html.escape(task_id)}</td><td>{html.escape(key)}</td><td>{verdict}</td></tr>")
    parts.append("</table></body></html>")
    return "".join(parts)
