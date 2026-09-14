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

# Copy each skill directory, but skip *-workspace siblings: those hold eval-run
# artifact trees (outputs/response.md, grading.json, timing.json per eval and
# per mutation candidate) needed for scoring, not for making the skill
# discoverable to a live session -- syncing them would be pure wasted I/O.
for entry in "$HERE"/.claude/skills/*/; do
    name="$(basename "$entry")"
    case "$name" in
        *-workspace) continue ;;
    esac
    cp -r "$entry" "$ROOT/.claude/skills/"
done

# cp -r only adds/overwrites -- it never prunes files removed at the source.
# mutate_skill.py's temporary *.orig backups must never linger in the mirror,
# and neither should a *-workspace dir synced by an older version of this script.
find "$ROOT/.claude/skills" -iname "*.orig" -delete
find "$ROOT/.claude/skills" -type d -iname "*-workspace" -exec rm -rf {} +

echo "Synced .claude/{commands,agents,skills} from $HERE to $ROOT"
