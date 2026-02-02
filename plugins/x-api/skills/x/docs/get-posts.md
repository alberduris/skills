Retrieves multiple posts by their IDs (up to 100). Maps to GET /2/tweets. Invoke via `node <base_directory>/x.js get-posts <id1,id2,...> [flags]`. Pass IDs as a single comma-separated argument. Output is JSON to stdout.

[!FLAGS] a) no flags — returns posts with default tweet fields (text, author_id, created_at, conversation_id, public_metrics) and expands author (name, username), outputting ONLY the post array. b) `--fields <comma-list>` — override default tweet fields. c) `--raw` — output the full API response envelope (data, includes, errors).

[!OUTPUT-SHAPE] Default produces an array of post objects. With `--raw`, wraps into the API envelope with `data` (posts) and `includes` (expanded users).
