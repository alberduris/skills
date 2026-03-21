---
description: Generate a compact single-story "EXTRA" edition — urgent, telegraphic, above-the-fold-only newspaper for a single subject
---
Load the newspaper-explainer skill. Read ./templates/broadsheet.html and ./references/css-patterns.md to absorb the canonical CSS class vocabulary and palette, but generate a REDUCED structure. Then generate an EXTRA edition for: $@

Extra edition output is ALWAYS opt-in — only generate when this command is invoked or the user explicitly asks for an extra, bulletin, or summary edition. The extra edition is the newspaper equivalent of a wire dispatch: one subject, maximum density, no filler.

The structure is strictly MASTHEAD (with "EXTRA EDITION" in the edition field) + TICKER (single scrolling headline) + ONE LEAD STORY (with drop cap, inset box, pull quote, column text — the full lead treatment) + COLOPHON. No sidebar, no secondary stories, no letters, no dispatch board. Everything that matters fits above the fold. The narrative should be telegraphic — authoritative, compressed, every sentence carrying information.

Gather facts with the same rigor as a full edition. NEVER EVER fabricate. Write to ~/.agent/newspapers/ and open in the browser.

$@
