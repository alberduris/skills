Look up a community by its ID. Maps to GET /2/communities/{id}. Invoke via `node <base_directory>/x.js community <id> [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns the community with all available fields (name, description, member_count, join_policy, access, created_at). b) `--raw` — outputs the full API response envelope.

[!OUTPUT-SHAPE] Produces the community object directly. With `--raw`, wraps into the API envelope with `data` and `errors`.
