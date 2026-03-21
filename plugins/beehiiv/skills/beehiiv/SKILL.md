---
name: beehiiv
description: Manage your Beehiiv newsletter — list and read posts, create drafts from Markdown/HTML files. 6-command skill for Beehiiv newsletter automation.
license: MIT
metadata:
  author: alberduris
  version: "0.1.0"
  tags: beehiiv, newsletter, email, posts, drafts, content, automation
allowed-tools: Bash(node *), Bash(npm *), Bash(npx *), Bash(ls *)
---

Beehiiv API v2 skill for managing newsletter posts and drafts. All commands go through a single entry point: `node <base_directory>/beehiiv.js <command> [flags]`. Each command has its own doc file with the full reference for flags and behavior.

[!SETUP] Before first use, check whether `<base_directory>/node_modules` exists. If it does NOT exist, run `npm install --prefix <base_directory>`. Then check whether `<base_directory>/dist/beehiiv.js` exists. If it does NOT exist, run `npm run build --prefix <base_directory>`. NEVER cd into the skill directory; use --prefix to target it without changing your working directory.

[!COMMANDS]

Reading:
a) `publications` — list all publications associated with the API key. @docs/publications.md.
b) `publication` — get a single publication's details and stats. @docs/publication.md.
c) `posts` — list posts with filters (status, tags, authors, audience, platform). This is the primary search mechanism. @docs/posts.md.
d) `get` — retrieve a single post by ID with full HTML content. @docs/get.md.

Writing:
e) `draft` — create a draft post from a title + optional .md/.html file. Enterprise-only endpoint (beta). @docs/draft.md.

Utility:
f) `templates` — list available post templates. @docs/templates.md.

[!CREDENTIALS] One variable is REQUIRED: `BEEHIIV_API_KEY`. One variable is OPTIONAL: `BEEHIIV_PUBLICATION_ID` (default publication — if set, commands use it automatically; if not, pass `--pub-id <id>`). They resolve from the first source that provides them: a) `.env.local` in cwd, b) `.env` in cwd, c) `.env.local` in the plugin directory, d) `.env` in the plugin directory, e) environment variables. Obtain the API key from the Beehiiv dashboard (Settings > Integrations > API).

[!PUB-ID] All commands except `publications` require a publication ID. If `BEEHIIV_PUBLICATION_ID` is set, it is used by default. Any command can override it with `--pub-id <id>`. To discover your publication ID, run `publications` first.

[!API-COVERAGE]
Covered resources:
- Publications: list, get (commands: publications, publication)
- Posts: list, get single, create as draft (commands: posts, get, draft)
- PostTemplates: list (command: templates)

NOT covered (future TODO):
- Subscriptions: list, create, get by email/id, update, delete, bulk actions, JWT token, tags
- Authors: list, get single
- Automations: list, get single, journeys list/get
- BulkSubscriptions: create, updates status
- ConditionSets: list, get single
- CustomFields: list, get, create, update, delete
- EmailBlasts: list, get single
- Engagements: list
- Polls: list, get single, responses
- PostAggregateStats: get
- ReferralProgram: get
- Segments: list, get, recalculate, members, results
- Tiers: list, get single
- Webhooks: list, get, create, update, delete, test
- AdvertisementOpportunities: list
