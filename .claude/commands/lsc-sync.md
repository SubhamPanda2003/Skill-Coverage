---
description: Copy this repo's .claude/{commands,agents,skills} to the workspace root, since Claude Code reads project commands/skills from the workspace root here, not from this nested repo. Run after adding or editing any lsc-* command, agent, or skill.
---

Run `bash Skill-Coverage/sync_workspace_root.sh` (or `bash sync_workspace_root.sh` if already inside `Skill-Coverage/`) and show me the output. This repo's `.claude/` is the source of truth -- if a `/lsc-*` command doesn't show up or seems out of date, this is the first thing to run, not a reason to edit the workspace-root copy directly.
