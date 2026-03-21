# Newspaper Explainer

Generate self-contained HTML broadsheet newspapers to explain any subject worth reporting — project status, reviews, dispatches, implementation plans, or anything else.

## Features

Broadsheet newspaper aesthetic with monochromatic ink-on-paper palette · Drop caps, pull quotes, column rules, scrolling ticker · Lead story with floating inset box and progress bar · Sidebar with status widgets and secondary articles · Letters & Correspondence section for decision dialogue · Dispatch Board for action items and notices · Dark mode (night edition) via prefers-color-scheme · Print-friendly · Fully self-contained single HTML file

## Commands

`generate-dispatch` — full newspaper edition on any subject · `diff-review` — diff analysis as investigative journalism · `plan-review` — plan feasibility as editorial assessment · `project-recap` — project status as evening edition · `generate-plan` — implementation plan as front-page reporting · `generate-extra` — compact single-story urgent edition · `fact-check` — verify newspaper claims against actual code/data · `share` — deploy to Vercel for instant public URL

## Install

```bash
npx skills add https://github.com/alberduris/skills --skill newspaper-explainer
```

## Usage

```
/newspaper-explainer:generate-dispatch explain the current state of the auth system
/newspaper-explainer:project-recap 2w
/newspaper-explainer:diff-review main
```

## Credits

Inspired by [@sambodanis](https://x.com/sambodanis)'s "The Foreman Dispatch" — the original newspaper-style agent reporting built for their personal orchestrator ([via @noampomsky](https://x.com/noampomsky/status/2035153535462252787)) — and by [visual-explainer](https://github.com/nicobailon/visual-explainer) by [@nicobailon](https://skills.sh/nicobailon/visual-explainer/visual-explainer) for the skill architecture.

## License

MIT
