Retrieves posts that mention the authenticated user. Maps to GET /2/users/:id/mentions. Invoke via `node <base_directory>/x.ts mentions [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns recent mentions. b) `--max-results <1-100>` — set number of results per page. c) `--next-token <token>` — pagination token from a previous response. d) `--start-time <ISO8601>` — oldest timestamp (inclusive). e) `--end-time <ISO8601>` — newest timestamp (exclusive).

[!OUTPUT-SHAPE] `data` is an array of posts.
