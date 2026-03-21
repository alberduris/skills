---
description: Generate a broadsheet newspaper edition reviewing a diff — before/after analysis presented as investigative journalism
---
Load the newspaper-explainer skill. Read ./templates/broadsheet.html and ./references/css-patterns.md to absorb the canonical structure, CSS class vocabulary, and palette. Then generate a broadsheet newspaper edition reviewing a diff.

Determine what to diff from $1: a) branch name means working tree vs that branch, b) commit hash means that specific commit via git show, c) HEAD means uncommitted changes only, d) PR number (e.g. #42) means gh pr diff, e) range (e.g. abc..def) means diff between two commits, f) no argument defaults to main. Gather ALL facts before writing HTML: run git diff --stat and --name-status for scope, read every changed file in full, identify new public API surface, check whether CHANGELOG and docs need updates, reconstruct decision rationale from commit messages or conversation history.

The LEAD STORY covers the core insight — WHY these changes exist, what problem they solve, not just what changed. The floating INSET BOX carries KPI metrics (lines added/removed, files changed, new modules). SECONDARY STORIES cover individual areas of change (UI, API, data layer, tests, config) as separate articles. The SIDEBAR reports housekeeping status (changelog updated, docs current, test coverage). LETTERS AND CORRESPONDENCE reconstructs the design decisions as dialogue — what was decided, why, what alternatives were considered. The DISPATCH BOARD surfaces action items: missing tests, documentation gaps, follow-up work needed. Code review findings (good patterns, bugs, tech debt) run as editorial analysis within the relevant articles.

NEVER EVER fabricate facts — every claim must be traceable to actual git output or file contents. Write to ~/.agent/newspapers/ and open in the browser.

Ultrathink.

$@
