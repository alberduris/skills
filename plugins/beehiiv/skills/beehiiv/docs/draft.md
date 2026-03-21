Creates a new draft post in the publication. Maps to POST /publications/{publicationId}/posts with status "draft". Invoke via `node <base_directory>/beehiiv.js draft "<title>" [flags]`. Output is JSON to stdout.

[!ENTERPRISE] This endpoint is currently in beta and only available to Enterprise users. Non-enterprise accounts will receive a 403 error. The command is implemented for forward-compatibility.

[!FLAGS] a) no flags — creates a draft with only the title. b) `--subtitle <text>` — set the subtitle. c) `--content-file <path>` — read the post body from a local file. Supports .html and .md/.markdown files (Markdown is auto-converted to HTML). d) `--content <html|->` — inline HTML body, or `-` to read from stdin. e) `--content-tags <comma-list>` — content tags for the post. f) `--template-id <id>` — post template ID (use `templates` to list available ones). g) `--slug <slug>` — custom URL slug for the web version. h) `--raw` — output the full API response envelope.

[!CONTENT-PRIORITY] If both `--content-file` and `--content` are provided, `--content-file` wins. For long content, always prefer `--content-file` over inline `--content` to avoid shell escaping issues.

[!WORKFLOW] Typical usage: write content as .md file, then `draft "My Title" --content-file ./post.md --subtitle "A subtitle" --content-tags "tag1,tag2"`. The draft appears in the Beehiiv dashboard ready for review and publishing.

[!OUTPUT-SHAPE] Returns the created post object with its id. Use this ID to find the draft in the Beehiiv dashboard.
