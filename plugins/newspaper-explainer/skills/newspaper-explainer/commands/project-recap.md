---
description: Generate a broadsheet newspaper edition recapping a project's recent activity, decisions, and current state
---
Load the newspaper-explainer skill. Read ./templates/broadsheet.html and ./references/css-patterns.md to absorb the canonical structure, CSS class vocabulary, and palette. Then generate a broadsheet newspaper edition recapping the project at the current working directory.

Determine the recency window from $1 (shorthand like 2w, 30d, 3m parsed to git --since format; default 2w if omitted or if $1 is free-form context). Gather facts BEFORE writing any HTML: a) project identity from README, package manifests, and top-level structure, b) recent git activity grouped by theme (features, fixes, refactors, infra) with commit narrative not raw log, c) current state via git status, open branches, TODO/FIXME in recently changed files, d) key decisions extracted from commit messages, plan docs, or conversation history, e) architecture snapshot of the modules and their relationships as they exist today.

The LEAD STORY covers the single most significant development in the window. SECONDARY STORIES cover supporting themes. The SIDEBAR carries project identity, key metrics (commits, files changed, contributors), and current system state. LETTERS AND CORRESPONDENCE works as a dialogue reconstructing key decisions and their rationale. The DISPATCH BOARD surfaces open TODOs, pending decisions, stale branches, and cognitive debt hotspots. The newspaper name and tagline should reflect the project identity.

NEVER EVER fabricate facts — every claim must be traceable to something you actually read or ran. Write to ~/.agent/newspapers/ and open in the browser.
