List a user's followers or the accounts they follow. Accepts a username or user ID. `followers` maps to GET /2/users/:id/followers. `following` maps to GET /2/users/:id/following. Invoke via `node <base_directory>/x.ts followers <username|id> [flags]` or `node <base_directory>/x.ts following <username|id> [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns users with default profile fields (name, username, bio, metrics, avatar, verification). b) `--max-results <1-1000>` — set number of results per page. c) `--next-token <token>` — pagination token from a previous response.

[!OUTPUT-SHAPE] `data` is an array of user objects.
