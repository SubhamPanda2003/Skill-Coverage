"""Deterministic parsing, segmentation, classification, discovery, and applicability."""
import re
from dataclasses import dataclass, field

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "for", "to",
    "of", "with", "that", "this", "is", "are", "use", "when", "needs", "always",
}

PRONOUN_GUARD = re.compile(r"^(it|this|that|these|those|they)\b", re.IGNORECASE)
CONJ_GUARD = re.compile(r"^(and|or|but)\s+if\b", re.IGNORECASE)
IF_THEN = re.compile(
    r"\bif\s+(?P<cond>.+?)\s+then\s+(?P<action>.+?)(?=\s+and\s+if\b|\s+or\s+if\b|\s*$)",
    re.IGNORECASE,
)
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
CHECKABLE_TOKEN = re.compile(
    r"\b\d+\s?(px|pt|em|rem|%|characters?|chars?)\b|\btabs\b|\bspaces\b|\bnewline\b",
    re.IGNORECASE,
)


def tokenize(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {w for w in words if w not in STOPWORDS}


def keyword_overlap(kws_a, kws_b):
    for a in kws_a:
        for b in kws_b:
            if len(a) >= 4 and len(b) >= 4 and (a == b or a in b or b in a):
                return True
            if a == b:
                return True
    return False


@dataclass
class Branch:
    id: str
    cond_text: str
    action_text: str
    start: int
    end: int
    cond_keywords: set = field(default_factory=set)


@dataclass
class Unit:
    id: str
    skill: str
    text: str
    start: int
    end: int
    type: str = "Judged"
    branches: list = field(default_factory=list)


def parse_skill_md(raw_text):
    """Split a SKILL.md into frontmatter fields + body text, per the agentskills.io spec."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw_text, re.DOTALL)
    if not m:
        raise ValueError("SKILL.md missing --- frontmatter block")
    fm_text, body = m.group(1), m.group(2)
    fm = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    if "name" not in fm or "description" not in fm:
        raise ValueError("SKILL.md frontmatter missing required 'name' or 'description'")
    return fm, body


def segment(skill_name, body):
    """Deterministic constraint-unit segmentation: markdown paragraphs -> sentences,
    with a fail-closed anaphora/conjunction guard that merges dangling clauses back
    into the unit they depend on, so no unit is ever a referentially broken fragment."""
    units = []
    pos = 0
    unit_idx = 0
    for para in re.split(r"\n\s*\n", body):
        para_start = body.index(para, pos)
        pos = para_start + len(para)
        stripped = para.strip()
        if not stripped or stripped.startswith("#"):
            continue  # headings / blank blocks are excluded, not constraint-bearing
        offset = body.index(stripped, para_start)
        sentences = [s for s in SENT_SPLIT.split(stripped) if s]
        cur_start = offset
        cur_text = sentences[0]
        for sent in sentences[1:]:
            sent_start = body.index(sent, cur_start + len(cur_text))
            if PRONOUN_GUARD.search(sent) or CONJ_GUARD.match(sent):
                # dangling reference -> fail closed, merge into the current unit
                cur_text = body[cur_start:sent_start + len(sent)]
            else:
                units.append(_make_unit(skill_name, unit_idx, body, cur_start, cur_text))
                unit_idx += 1
                cur_start = sent_start
                cur_text = sent
        units.append(_make_unit(skill_name, unit_idx, body, cur_start, cur_text))
        unit_idx += 1
    return units


def _make_unit(skill_name, idx, body, start, text):
    text = text.strip()
    start = body.index(text, start)
    end = start + len(text)
    unit = Unit(id=f"{skill_name}#u{idx}", skill=skill_name, text=text, start=start, end=end)
    unit.type = "Verifiable" if CHECKABLE_TOKEN.search(text) else "Judged"
    branch_matches = list(IF_THEN.finditer(text))
    if branch_matches:
        for bi, bm in enumerate(branch_matches):
            b_start, b_end = bm.start(), bm.end()
            branch_text = text[b_start:b_end]
            cond_kw = tokenize(bm.group("cond"))
            unit.branches.append(Branch(
                id=f"{unit.id}#b{bi}", cond_text=bm.group("cond"), action_text=bm.group("action"),
                start=start + b_start, end=start + b_end, cond_keywords=cond_kw,
            ))
    else:
        unit.branches.append(Branch(
            id=f"{unit.id}#b0", cond_text="(unconditional)", action_text=text,
            start=start, end=end, cond_keywords=set(),
        ))
    return unit


def load_skills(skill_dirs):
    """skill_dirs: {skill_name: path_to_SKILL.md}. Returns {name: {fm, body, units}}."""
    skills = {}
    for name, path in skill_dirs.items():
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        fm, body = parse_skill_md(raw)
        assert fm["name"] == name, f"frontmatter name '{fm['name']}' != directory name '{name}'"
        skills[name] = {
            "description": fm["description"],
            "keywords": tokenize(fm["name"] + " " + fm["description"]),
            "body": body,
            "units": segment(name, body),
        }
    return skills


def discover(task_text, skills):
    """Two-stage discovery/activation per the agentskills.io spec, collapsed into one
    deterministic lexical check: a skill activates iff the task text overlaps its
    name+description keyword set."""
    task_kw = tokenize(task_text)
    activated = set()
    for name, skill in skills.items():
        if keyword_overlap(task_kw, skill["keywords"]):
            activated.add(name)
    return activated


def applicable_branches(task_text, unit):
    task_kw = tokenize(task_text)
    hits = []
    for br in unit.branches:
        if not br.cond_keywords or keyword_overlap(task_kw, br.cond_keywords):
            hits.append(br)
    return hits
