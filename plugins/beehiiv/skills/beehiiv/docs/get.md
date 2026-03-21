Retrieves a single post by ID with full content. Maps to GET /publications/{publicationId}/posts/{postId}. Invoke via `node <base_directory>/beehiiv.js get <postId> [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns the post with free_web_content expanded by default, so you can read the full HTML body. b) `--expand <comma-list>` — override expand fields (stats, free_web_content, free_email_content, free_rss_content, premium_web_content, premium_email_content). c) `--raw` — output the full API response envelope.

[!OUTPUT-SHAPE] Default produces the post object directly with metadata (id, title, subtitle, authors, status, slug, web_url, etc.) and content.free.web containing the rendered HTML. The HTML is the full post body as it appears on the web.
