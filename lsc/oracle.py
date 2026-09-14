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


def _code_content(artifact):
    """Text inside markdown code fences, or the whole artifact if there are
    none -- scoping a line-length check to code avoids the exact false-negative
    the docstring-length checker had, where a stray sentence outside the fence
    tripped a check that was only ever meant to apply to code/docstring text."""
    blocks = re.findall(r"```(?:\w*\n)?(.*?)```", artifact, re.DOTALL)
    return "\n".join(blocks) if blocks else artifact


def _strip_triple_quoted(artifact):
    return re.sub(r'""".*?"""', "", artifact, flags=re.DOTALL)


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

    # 25-skill expansion (docs/results.md Part 5) -- each predicted fight/align
    # with a plausible pretrained default; see the design table there.
    ("date-format", 0, 0): lambda art: _has_token(art, r"\b\d{2}/\d{2}/\d{4}\b"),
    ("quote-style", 0, 0): lambda art: (
        _has_token(art, r"'[^'\"\n]+'") and not re.search(r'"[^"\n]+"', _strip_triple_quoted(art))
    ),
    ("variable-naming", 0, 0): lambda art: (
        re.search(r"\b[a-z]+[A-Z][a-zA-Z0-9]*\s*=(?!=)", art) is not None
        and re.search(r"\b[a-z][a-z0-9]*_[a-z][a-z0-9_]*\s*=(?!=)", art) is None
    ),
    ("line-length-limit", 0, 0): lambda art: max(
        (len(l) for l in _code_content(art).splitlines()), default=0
    ) <= 60,
    ("currency-format", 0, 0): lambda art: _has_token(art, r"\b\d{1,3}(\.\d{3})*,\d{2}\b"),
    ("boolean-naming", 0, 0): lambda art: not re.search(r"\b(is|has|should)_[a-zA-Z_]+\b", art),
    ("measurement-units", 0, 0): lambda art: (
        _has_token(art, r"\b(miles?|lbs?|pounds?)\b") and not _has_token(art, r"\b(kilometers?|km|kilograms?|kg)\b")
    ),
    ("string-concat", 0, 0): lambda art: not _has_token(art, r"f['\"]") and "+" in art,
    ("test-naming", 0, 0): lambda art: (
        re.search(r"def\s+should_\w*\s*\(", art) is not None
        and re.search(r"def\s+test_\w*\s*\(", art) is None
    ),
    ("em-dash-ban", 0, 0): lambda art: "—" not in art,
    ("docstring-quotes", 0, 0): lambda art: '"""' in art and "'''" not in art,
    ("constant-naming", 0, 0): lambda art: re.search(r"^[A-Z][A-Z0-9_]*\s*=", art, re.MULTILINE) is not None,
    ("mutable-default-ban", 0, 0): lambda art: re.search(
        r"def\s+\w+\([^)]*=\s*(\[\]|\{\}|list\(\)|dict\(\))", art
    ) is None,
    ("fstring-required", 0, 0): lambda art: _has_token(art, r"f['\"]"),
    ("oxford-comma", 0, 0): lambda art: _has_token(art, r",\s+and\s+\w+"),
    ("trailing-comma", 0, 0): lambda art: re.search(r",\s*\n\s*[\]\)\}]", art) is not None,
    ("error-period", 0, 0): lambda art: re.search(r"raise\s+\w+\(\s*f?[\"'][^\"']*\.[\"']\s*\)", art) is not None,
    ("semicolon-ban", 0, 0): lambda art: re.search(r";\s*$", art, re.MULTILINE) is None,

    # Deliberately arbitrary instructions with no plausible grounding in any
    # real convention -- a positive control for mutation-adequacy itself: if
    # the model complies at all, it can only be because it read the skill,
    # so deletion should kill these every time. See docs/results.md Part 6.
    ("variable-naming", 1, 0): lambda art: re.search(r"\bpanda[A-Za-z0-9_]*\s*=(?!=)", art) is not None,
    ("string-concat", 1, 0): lambda art: _has_vowelless_string(art),
}


def _has_vowelless_string(artifact):
    """Best-effort check for 'replace vowels with x' -- the instruction is
    genuinely ambiguous (vowels in which statement? replaced how?), so this
    looks for a string literal with 3+ letters and no vowels among them, the
    strongest available signal of deliberate vowel removal."""
    for s in re.findall(r"[\"']([^\"'\n]{3,})[\"']", artifact):
        letters = [c for c in s if c.isalpha()]
        if len(letters) >= 3 and not any(c.lower() in "aeiou" for c in letters):
            return True
    return False


def evidence_for(skill, unit_index, branch_index, artifact):
    """Short, mechanically-true evidence string for a Verifiable unit, derived
    by re-running the same check CHECKERS uses and reporting what it found.
    Used to keep grading.json's evidence field honest and regeneratable --
    never guessed, never independently re-derived by hand."""
    key = (skill, unit_index, branch_index)
    if key == ("text-styling", 0, 0):
        m = re.search(r"20\s?px", artifact, re.IGNORECASE)
        return f"Found {m.group(0)!r} in artifact" if m else "No '20px' (or '20 px') found in artifact"
    if key == ("text-styling", 0, 1):
        m = re.search(r"30\s?px", artifact, re.IGNORECASE)
        return f"Found {m.group(0)!r} in artifact" if m else "No '30px' (or '30 px') found in artifact"
    if key == ("indent-tabs", 0, 0):
        tabs, spaces = indent_style(artifact)
        return f"tab-indented lines={tabs}, space-indented lines={spaces}"
    if key == ("indent-tabs", 1, 0):
        return "Artifact text ends with a newline" if artifact.endswith("\n") else "Artifact text does not end with a newline"
    if key == ("indent-spaces", 0, 0):
        tabs, spaces = indent_style(artifact)
        return f"space-indented lines={spaces}, tab-indented lines={tabs}"
    if key == ("commit-messages", 1, 0):
        first = artifact.splitlines()[0] if artifact.splitlines() else ""
        return f"First line is {len(first)} chars: {first!r}"
    if key == ("error-handling", 0, 0):
        m = re.search(r"except\s*:", artifact)
        return f"Found bare 'except:' at match {m.group(0)!r}" if m else "No bare 'except:' clause found"
    if key == ("error-handling", 1, 0):
        m = re.search(r"raise\s+\w+\([^)]*\)\s+from\s+\w+", artifact)
        return f"Found chained raise: {m.group(0)!r}" if m else "No 'raise X(...) from err' pattern found"
    if key == ("docstring-style", 2, 0):
        return "'Args:' found in artifact" if "Args:" in artifact else "'Args:' not found in artifact"
    if key == ("docstring-style", 2, 1):
        return "'Raises:' found in artifact" if "Raises:" in artifact else "'Raises:' not found in artifact"
    if key == ("docstring-style", 3, 0):
        lens = _docstring_line_lengths(artifact)
        longest = max(lens, default=0)
        return f"Longest docstring line is {longest} chars (limit 79), across {len(lens)} docstring lines"
    if key == ("date-format", 0, 0):
        m = re.search(r"\b\d{2}/\d{2}/\d{4}\b", artifact)
        return f"Found DD/MM/YYYY-shaped date {m.group(0)!r}" if m else "No DD/MM/YYYY-shaped date found"
    if key == ("quote-style", 0, 0):
        single = re.search(r"'[^'\"\n]+'", artifact)
        double = re.search(r'"[^"\n]+"', _strip_triple_quoted(artifact))
        return f"single-quoted string found: {bool(single)}, double-quoted string found: {bool(double)}"
    if key == ("variable-naming", 0, 0):
        camel = re.search(r"\b[a-z]+[A-Z][a-zA-Z0-9]*\s*=(?!=)", artifact)
        snake = re.search(r"\b[a-z][a-z0-9]*_[a-z][a-z0-9_]*\s*=(?!=)", artifact)
        return f"camelCase assignment found: {bool(camel)}, snake_case assignment found: {bool(snake)}"
    if key == ("line-length-limit", 0, 0):
        lines = _code_content(artifact).splitlines()
        longest = max((len(l) for l in lines), default=0)
        return f"Longest code line is {longest} chars (limit 60)"
    if key == ("currency-format", 0, 0):
        m = re.search(r"\b\d{1,3}(\.\d{3})*,\d{2}\b", artifact)
        return f"Found European-style amount {m.group(0)!r}" if m else "No period-thousands/comma-decimal amount found"
    if key == ("boolean-naming", 0, 0):
        m = re.search(r"\b(is|has|should)_[a-zA-Z_]+\b", artifact)
        return f"Found banned prefix in identifier {m.group(0)!r}" if m else "No is_/has_/should_ prefixed identifier found"
    if key == ("measurement-units", 0, 0):
        imperial = _has_token(artifact, r"\b(miles?|lbs?|pounds?)\b")
        metric = _has_token(artifact, r"\b(kilometers?|km|kilograms?|kg)\b")
        return f"imperial unit found: {imperial}, metric unit found: {metric}"
    if key == ("string-concat", 0, 0):
        has_fstring = _has_token(artifact, r"f['\"]")
        return f"f-string found: {has_fstring}, '+' present: {'+' in artifact}"
    if key == ("test-naming", 0, 0):
        should_def = re.search(r"def\s+should_\w*\s*\(", artifact)
        test_def = re.search(r"def\s+test_\w*\s*\(", artifact)
        return f"should_-prefixed test def found: {bool(should_def)}, test_-prefixed def found: {bool(test_def)}"
    if key == ("em-dash-ban", 0, 0):
        return "No em dash found" if "—" not in artifact else "Em dash character found in artifact"
    if key == ("docstring-quotes", 0, 0):
        triple_double = '"""' in artifact
        triple_single = "'''" in artifact
        return f"triple double-quote found: {triple_double}, triple single-quote found: {triple_single}"
    if key == ("constant-naming", 0, 0):
        m = re.search(r"^[A-Z][A-Z0-9_]*\s*=", artifact, re.MULTILINE)
        return f"Found uppercase constant assignment {m.group(0)!r}" if m else "No uppercase module-level constant assignment found"
    if key == ("mutable-default-ban", 0, 0):
        m = re.search(r"def\s+\w+\([^)]*=\s*(\[\]|\{\}|list\(\)|dict\(\))", artifact)
        return f"Found mutable default argument: {m.group(0)!r}" if m else "No mutable default argument found"
    if key == ("fstring-required", 0, 0):
        found = _has_token(artifact, r"f['\"]")
        return f"f-string token found: {found}"
    if key == ("oxford-comma", 0, 0):
        m = re.search(r",\s+and\s+\w+", artifact)
        return f"Found Oxford comma before 'and': {m.group(0)!r}" if m else "No comma found immediately before 'and'"
    if key == ("trailing-comma", 0, 0):
        m = re.search(r",\s*\n\s*[\]\)\}]", artifact)
        return "Found trailing comma before a closing bracket on the next line" if m else "No trailing comma found before a closing bracket"
    if key == ("error-period", 0, 0):
        m = re.search(r"raise\s+\w+\(\s*f?[\"'][^\"']*\.[\"']\s*\)", artifact)
        return "Raised error message ends with a period" if m else "No raised error message ending in a period found"
    if key == ("semicolon-ban", 0, 0):
        m = re.search(r";\s*$", artifact, re.MULTILINE)
        return "No line ends with a semicolon" if not m else "A line ends with a semicolon"
    if key == ("variable-naming", 1, 0):
        m = re.search(r"\bpanda[A-Za-z0-9_]*\s*=(?!=)", artifact)
        return f"Found panda-prefixed identifier {m.group(0)!r}" if m else "No identifier starting with 'panda' was assigned"
    if key == ("string-concat", 1, 0):
        found = _has_vowelless_string(artifact)
        return f"vowel-free string literal (3+ letters) found: {found}"
    return "(no evidence generator registered for this key)"


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
