Lists the authenticated user's own posts that others reposted: each post's `author` is the account itself, and the reposters are not in the output; `reposters <tweet_id>` lists who reposted each one. Maps to GET /2/users/reposts_of_me. Invoke via `node <base_directory>/x.ts reposts-of-me [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns your posts that others recently reposted. b) `--max-results <1-100>` — set number of results per page. c) `--next-token <token>` — pagination token from a previous response.

[!OUTPUT-SHAPE] `data` is an array of posts.
