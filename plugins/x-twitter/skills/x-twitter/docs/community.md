Look up a community by its ID. Maps to GET /2/communities/{id}. Invoke via `node <base_directory>/x.ts community <id> [flags]`. Output is JSON to stdout.

[!FLAGS] No flags. Returns the community with all available fields (name, description, member_count, join_policy, access, created_at).

[!OUTPUT-SHAPE] `data` is the community object.
