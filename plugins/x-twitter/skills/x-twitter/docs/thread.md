Retrieves a full thread (conversation) given any tweet ID from within it. Automatically resolves the conversation_id, fetches all tweets via search, paginates, deduplicates, and returns them sorted chronologically. Invoke via `node <base_directory>/x.js thread <tweet_id> [flags]`. Output is JSON to stdout.

[!HOW-IT-WORKS] 1) Fetches the given tweet to obtain its conversation_id (always equals the root tweet's ID). 2) Searches `conversation_id:<id>` to collect all tweets in the conversation (auto-paginates). 3) Ensures the root tweet is included even if outside the search window. 4) Deduplicates and sorts chronologically.

[!FLAGS] a) no flags — returns the full thread using recent search (last 7 days). b) `--all` — use full archive search instead of recent (requires `X_API_BEARER_TOKEN`). Use this for threads older than 7 days. c) `--raw` — output wraps into `{ data: [...] }` envelope.

[!OUTPUT-SHAPE] Default produces an array of tweet objects sorted oldest-first. Each tweet includes default fields (text, author_id, created_at, conversation_id, public_metrics, referenced_tweets, in_reply_to_user_id) with expanded author (name, username). If recent search returned very few results, a `hint` field is included suggesting `--all`.

[!IMPORTANT] This is the correct way to read a thread. Do NOT use `search "conversation_id:..."` manually — the `thread` command handles everything automatically (resolution, pagination, root tweet inclusion, chronological sorting).
