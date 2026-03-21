---
name: newspaper-explainer
description: Generate self-contained HTML broadsheet newspapers to explain any subject worth reporting — project status, reviews, dispatches, reports, or anything else.
license: MIT
metadata:
  author: alberduris
  version: "0.2.0"
---

This skill generates single-file HTML pages that present any subject worth explaining as broadsheet newspaper editions. Every page follows ONE fixed aesthetic — the broadsheet — so variation comes from CONTENT (what is being reported, which sections are relevant, what the edition covers), not from visual style or chromatic direction. Read ./templates/broadsheet.html before generating any page; it is the canonical reference for structure, CSS class vocabulary, typographic stack, and palette.

A newspaper page is assembled from structural elements selected based on what the content demands: a) MASTHEAD carrying the publication name, date, volume/issue number, and edition tagline, b) TICKER as a scrolling marquee summarizing the top headlines, c) LEAD STORY occupying the dominant grid position with drop cap, optional floating inset box with progress bar, pull quote between rules, and multi-column continuation text, d) SIDEBAR with bordered status widgets and compact secondary articles, e) SECONDARY STORIES row in a multi-column grid separated by column rules, f) LETTERS AND CORRESPONDENCE presenting timestamped dialogue in a question-and-response cadence, g) DISPATCH BOARD with classified-ad-style cards for action items, notices, and advisories, h) COLOPHON footer with publication metadata. Include only the sections that serve the content being reported.

[!IMPORTANT]: The palette is MONOCHROMATIC: warm cream paper, near-black ink, color used ONLY in status badges and dot indicators. NEVER EVER introduce gradients, colored section backgrounds, decorative color, or any chromatic element beyond the restrained badge accents defined in the template. Typography is FIXED at four tiers: display serif for masthead and headlines, body serif for article text, system sans for labels and metadata, monospace for inline code references. Do not substitute or rotate fonts across generations.

The output is always a single self-contained HTML file with all CSS inline, no external assets beyond CDN font links. Write to ~/.agent/newspapers/ using a descriptive filename derived from the content. Open the result in the browser and tell the user the file path.
