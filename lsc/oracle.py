"""Compliance oracles: deterministic assertions for Verifiable units, a judge
stub for Judged units. Keyed by (skill, unit_index, branch_index)."""
import re


def _has_token(artifact, pattern):
    return re.search(pattern, artifact, re.IGNORECASE) is not None


def indent_style(artifact):
    tab_lines = sum(1 for l in artifact.splitlines() if l.startswith("\t"))
    space_lines = sum(1 for l in artifact.splitlines() if re.match(r"^ {2,}\S", l))
    return tab_lines, space_lines


def _docstring_line_lengths(artifact):
    bodies = re.findall(r'"""(.*?)"""', artifact, re.DOTALL)
    bodies += re.findall(r"'''(.*?)'''", artifact, re.DOTALL)
    return [len(l) for body in bodies for l in body.splitlines()]


CHECKERS = {
    ("text-styling", 0, 0): lambda art: _has_token(art, r"20\s?px"),   # blue branch
    ("text-styling", 0, 1): lambda art: _has_token(art, r"30\s?px"),   # red branch
    ("indent-tabs", 0, 0): lambda art: indent_style(art)[0] > 0 and indent_style(art)[1] == 0,
    ("indent-tabs", 1, 0): lambda art: art.endswith("\n"),
    ("indent-spaces", 0, 0): lambda art: indent_style(art)[1] > 0 and indent_style(art)[0] == 0,
    ("commit-messages", 1, 0): lambda art: len(art.splitlines()[0]) <= 50,
    ("error-handling", 0, 0): lambda art: not _has_token(art, r"except\s*:"),           # no bare except
    ("error-handling", 1, 0): lambda art: _has_token(art, r"raise\s+\w+\([^)]*\)\s+from\s+\w+"),
    ("docstring-style", 2, 0): lambda art: "Args:" in art,     # documents parameters
    ("docstring-style", 2, 1): lambda art: "Raises:" in art,   # documents exceptions
    ("docstring-style", 3, 0): lambda art: max(_docstring_line_lengths(art), default=0) <= 79,
}


def evaluate(skill, unit_index, branch_index, artifact, judged_verdicts=None):
    """Returns 'Pass' or 'Fail'. Deterministic where a checker exists; otherwise
    looks up a pre-validated Judged verdict supplied by the caller (standing in for
    the LLM-judge-with-human-validation step described in the methodology)."""
    key = (skill, unit_index, branch_index)
    if key in CHECKERS:
        return "Pass" if CHECKERS[key](artifact) else "Fail"
    if judged_verdicts and key in judged_verdicts:
        return judged_verdicts[key]
    raise KeyError(f"no oracle (deterministic or judged) registered for {key}")


def is_verifiable(skill, unit_index, branch_index):
    return (skill, unit_index, branch_index) in CHECKERS
