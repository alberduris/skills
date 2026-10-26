Lists posts by other users that are reposts of the authenticated user's posts. Maps to GET /2/users/reposts_of_me. Invoke via `node <base_directory>/x.ts reposts-of-me [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns recent reposts of your posts. b) `--max-results <1-100>` — set number of results per page. c) `--next-token <token>` — pagination token from a previous response.

[!OUTPUT-SHAPE] `data` is an array of posts.
