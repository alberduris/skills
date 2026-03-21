---
description: Generate a broadsheet newspaper edition reviewing a plan against the current codebase — feasibility assessment as investigative reporting
---
Load the newspaper-explainer skill. Read ./templates/broadsheet.html and ./references/css-patterns.md to absorb the canonical structure, CSS class vocabulary, and palette. Then generate a broadsheet newspaper edition reviewing a plan document against the actual codebase.

The plan file is $1 (path to a markdown plan, spec, or RFC). The codebase is $2 if provided, otherwise the current working directory. Gather ALL facts before writing HTML: a) read the plan in full and extract every proposed change, assumption, and scope boundary, b) read every file the plan references AND files that import or depend on those files, c) map the blast radius — what callers, tests, configs, and public API surface are affected, d) cross-reference plan vs code — does every file, function, and type the plan mentions actually exist and behave as described.

The LEAD STORY presents the plan's core thesis and the assessment verdict (viable, risky, incomplete, etc.). The floating INSET BOX carries impact metrics (files to modify, files to create, estimated scope, test coverage). SECONDARY STORIES cover individual areas of change as separate articles, each with a side-by-side current-vs-planned comparison. The SIDEBAR reports completeness indicators (does the plan cover tests, docs, migration, rollback). LETTERS AND CORRESPONDENCE reconstructs rationale gaps — changes where the plan says WHAT but not WHY, presented as unanswered questions to the plan author. The DISPATCH BOARD surfaces risks: edge cases not addressed, assumptions that need verification, ordering dependencies, cognitive complexity hotspots with concrete mitigation suggestions.

NEVER EVER fabricate facts — every claim must be traceable to the plan document or actual file contents. Write to ~/.agent/newspapers/ and open in the browser.

Ultrathink.

$@
