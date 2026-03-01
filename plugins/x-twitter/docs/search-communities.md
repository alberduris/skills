Searches communities matching a keyword query. Maps to GET /2/communities/search. Invoke via `node <base_directory>/x.js search-communities "<query>" [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns up to 10 matching communities with all available fields (name, description, member_count, join_policy, access, created_at). b) `--max-results <10-100>` — set number of results per page. c) `--next-token <token>` — pagination token from a previous response. d) `--raw` — output the full API response envelope.

[!OUTPUT-SHAPE] Default produces an array of community objects. With `--raw`, wraps into the API envelope with `data` and `meta` (next_token for pagination).
