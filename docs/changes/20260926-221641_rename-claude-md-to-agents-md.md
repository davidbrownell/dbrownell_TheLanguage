---
type: Change
title: Replaced CLAUDE.md with AGENTS.md
description: Moved coding-agent instructions from the Claude-specific CLAUDE.md to the tool-neutral AGENTS.md and updated them to python_development template v0.8.0.
status: current
generated: { by: claude-opus-5-5, at: 2026-09-26T22:16:42Z }
tags: [config, agents, documentation]
sources:
  - id: agents-md
    resource: AGENTS.md
    title: Coding-agent instructions
---

# Change

- Deleted `CLAUDE.md` and added `AGENTS.md`.
- Template version header changed from `0.6.0` to `python_development Version: 0.8.0`.
- "SOLID" reworded to "SOLID design principles".
- Added a `General` section under Python Development: run `python`-related tasks using `uv`.

# Rationale

`AGENTS.md` is the cross-agent convention, so the instructions apply to any coding agent rather than only Claude Code.

# Impact

Claude Code loads `CLAUDE.md`, not `AGENTS.md`; no `CLAUDE.md` shim was added, so Claude Code sessions in this repository no longer receive these instructions automatically. This was an intentional decision.
