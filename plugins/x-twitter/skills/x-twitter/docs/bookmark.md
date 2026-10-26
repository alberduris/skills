Lists the authenticated user's bookmarks. `bookmarks` maps to GET /2/users/:id/bookmarks, which accepts OAuth 1.0a user context. Invoke via `node <base_directory>/x.ts bookmarks [flags]`. Output is JSON to stdout.

[!READ-ONLY] The CLI cannot add or remove bookmarks, and has no `bookmark` or `unbookmark` command. POST /2/users/:id/bookmarks and DELETE /2/users/:id/bookmarks/:tweet_id accept exactly one auth scheme, OAuth 2.0 user context (`OAuth2UserToken`), and no credential this CLI reads (`X_API_KEY`/`X_API_SECRET`/`X_ACCESS_TOKEN`/`X_ACCESS_TOKEN_SECRET`/`X_API_BEARER_TOKEN`) provides it. Reaching them requires an OAuth 2.0 user-context flow (browser authorization with PKCE, token storage, and refresh, with scopes `bookmark.write`, `offline.access`), which would add stateful auth to an otherwise stateless CLI for two endpoints.

[!FLAGS] a) `--max-results <1-100>` — set number of results per page. b) `--next-token <token>` — pagination token.

[!OUTPUT-SHAPE] `data` is an array of posts.
