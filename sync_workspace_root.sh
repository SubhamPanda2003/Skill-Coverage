#!/bin/bash
# Claude Code's live session in this environment reads project commands/agents/skills
# from the *workspace root* (d:\RandomExperiments), not from this nested repo's own
# .claude/ directory. Run this after adding or editing anything under .claude/ here,
# so the workspace root copy stays current. This repo's .claude/ is the source of
# truth; the workspace root copy is a derived mirror -- never edit the mirror directly.
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

mkdir -p "$ROOT/.claude/commands" "$ROOT/.claude/agents" "$ROOT/.claude/skills"
cp "$HERE"/.claude/commands/*.md "$ROOT/.claude/commands/"
cp "$HERE"/.claude/agents/*.md "$ROOT/.claude/agents/"
cp -r "$HERE"/.claude/skills/* "$ROOT/.claude/skills/"

# cp -r only adds/overwrites -- it never prunes files removed at the source.
# mutate_skill.py's temporary *.orig backups must never linger in the mirror.
find "$ROOT/.claude/skills" -iname "*.orig" -delete

echo "Synced .claude/{commands,agents,skills} from $HERE to $ROOT"
