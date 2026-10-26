Retrieves one or more posts by ID. Pass a single ID or comma-separated IDs (up to 100). Maps to GET /2/tweets. Invoke via `node <base_directory>/x.ts get <id> [flags]` or `node <base_directory>/x.ts get <id1,id2,...>`. Output is JSON to stdout.

[!FLAGS] No flags.

[!OUTPUT-SHAPE] `data` is an array of posts, for one ID as for many. An ID X cannot return (deleted, protected, nonexistent) is left out of `data` and named in `errors`.
