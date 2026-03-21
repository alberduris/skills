---
description: Generate a broadsheet newspaper edition presenting an implementation plan for a feature — specification as front-page reporting
---
Load the newspaper-explainer skill. Read ./templates/broadsheet.html and ./references/css-patterns.md to absorb the canonical structure, CSS class vocabulary, and palette. Then generate a broadsheet newspaper edition presenting a comprehensive implementation plan for: $@

Data gathering — understand the context before designing: a) parse the feature request extracting core problem, desired behavior, constraints, and scope boundaries, b) read the relevant codebase identifying files that need modification, existing patterns, related functionality, types and APIs to conform to, c) understand extension points (hooks, event systems, plugin architectures, configs, public APIs), d) check for prior art (similar features already implemented, existing code to reuse or extend).

Design phase — work through the implementation before writing HTML: a) state design (new state variables, existing state affected, state machine if behavior has multiple modes), b) API design (commands, functions, endpoints, signatures, error cases), c) integration design (interaction with existing functionality, hooks, events), d) edge cases (concurrent operations, error conditions, boundary values).

Verification checkpoint — before generating HTML, produce a structured fact sheet covering every state variable with type and purpose, every function/API with signature, every file needing modification with specific changes, every edge case with expected behavior, every assumption the plan relies on. Verify each against the code. Mark unverifiable items as uncertain. This fact sheet is your source of truth during HTML generation.

The LEAD STORY presents the feature's core problem and the proposed solution as investigative reporting. The floating INSET BOX carries scope metrics (files to modify, new functions, estimated complexity). SECONDARY STORIES cover individual design areas as separate articles: state design, API surface, integration points. The SIDEBAR presents the current-vs-proposed comparison as a structured widget and lists file references. LETTERS AND CORRESPONDENCE presents edge cases as questions and their resolutions. The DISPATCH BOARD surfaces implementation warnings (backward compatibility, performance considerations), test requirements grouped by category, and critical assumptions that need validation.

NEVER EVER fabricate facts — every claim must be traceable to actual code or the feature request. Write to ~/.agent/newspapers/ and open in the browser.

Ultrathink.

$@
