Retrieves a single post by its ID. Maps to GET /2/tweets/:id. Invoke via `node <base_directory>/x.js get-post <id> [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns the post with default tweet fields (text, author_id, created_at, conversation_id, public_metrics) and expands author (name, username), outputting ONLY the post object. b) `--fields <comma-list>` — override default tweet fields. c) `--raw` — output the full API response envelope (data, includes, errors).

[!OUTPUT-SHAPE] Default produces the post object directly. With `--raw`, wraps into the API envelope with `data` (post) and `includes` (expanded users).
