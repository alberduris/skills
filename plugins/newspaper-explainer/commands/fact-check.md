---
description: Verify the factual accuracy of a generated newspaper against actual code, git history, and data — correct inaccuracies in place
---
Load the newspaper-explainer skill. Read ./templates/broadsheet.html and ./references/css-patterns.md to match the existing page's styling when inserting the verification summary. Then verify the factual accuracy of the target file.

The target is $1 (explicit path to an HTML file; if omitted, verify the most recently modified file in ~/.agent/newspapers/). This is a FACT-CHECKER, not a re-review — it does not second-guess analysis, opinions, or editorial judgments. It verifies that data presented matches reality, corrects what does not, and leaves everything else alone.

Extract every verifiable claim from the file: a) quantitative figures (line counts, file counts, function counts, percentages), b) names (functions, types, modules, file paths referenced), c) behavioral descriptions (what code does, how things work, before/after comparisons), d) structural claims (architecture, dependencies, import chains), e) temporal claims (git history, commit attributions, timeline). Skip subjective analysis. For each claim, go to the source — re-read files, re-run git commands, compare output against the newspaper's assertions. Classify each as CONFIRMED, CORRECTED (note what was wrong and the correct value), or UNVERIFIABLE.

Correct inaccuracies IN PLACE using surgical text replacements — fix numbers, names, paths, behavior descriptions, before/after swaps. Preserve layout, CSS, and structure. After corrections, insert a compact verification summary section at the bottom of the page matching the existing styling: total claims checked, confirmed count, corrections made with brief descriptions, unverifiable claims flagged. Tell the user what was checked, what was corrected, and open the file in the browser.

$@
