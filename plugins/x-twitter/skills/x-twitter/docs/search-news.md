Searches trending news stories matching a query (GET /2/news/search). Returns AI-generated news summaries with headlines, categories, keywords, and related posts. Invoke via `node <base_directory>/x.ts search-news "<query>" [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns up to 10 results with default news fields (category, cluster_posts_results, contexts, disclaimer, hook, keywords, name, summary, updated_at). b) `--max-results <1-100>` — set number of results (default 10). c) `--max-age-hours <1-720>` — maximum age of news stories in hours (default 168, i.e. 7 days). d) `--fields <comma-list>` — override default news fields.

[!OUTPUT-SHAPE] `data` is an array of news objects with headline (name), summary, category, keywords, and contexts.
