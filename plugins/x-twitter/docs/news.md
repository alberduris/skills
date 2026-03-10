Retrieves a single news story by ID (GET /2/news/{id}). Returns the full news object with headline, summary, category, related posts, and contextual data. Invoke via `node <base_directory>/x.js news <id> [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns the news story with default fields (category, cluster_posts_results, contexts, disclaimer, hook, keywords, name, summary, updated_at). b) `--fields <comma-list>` — override default news fields. c) `--raw` — output the full API response envelope.

[!OUTPUT-SHAPE] Default produces a single news object. With `--raw`, wraps into the full API response envelope.
