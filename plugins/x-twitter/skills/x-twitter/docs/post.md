Creates a new post (tweet, reply, or quote tweet). Maps to POST /2/tweets. Invoke via `node <base_directory>/x.js post "<text>" [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — creates a standalone tweet with the given text. b) `--reply-to <id>` — makes this post a reply to the specified post ID. c) `--quote <id>` — makes this a quote tweet of the specified post ID. d) `--reply-settings <following|mentionedUsers|subscribers|verified>` — restrict who can reply. e) `--paid-partnership` — labels the post as paid promotion. Verified end-to-end: the created post reads back with `paidPartnership: true`.

[!THREADS] To create a thread, post the first tweet, capture its ID from the response, then use `--reply-to <id>` for each subsequent tweet in the chain.

[!REPLY-LIMITS] X's changelog (2026-02-23) states that programmatic replies are only permitted when the original post's author has "summoned" the replier, by @mentioning that account or quoting one of its posts. Status: UNCONFIRMED. Replying inside a conversation the authenticated account already participates in does work; the restricted case — replying to an unrelated third party — has not been exercised. Treat it as reported-by-X, not established: two other changelog claims from the same period do not hold in practice, as like/follow/quote writes still work and retweets still appear in search results.

[!COST] Replying to or quoting a post inserts a `t.co` URL into the post text. X announced (2026-04-16) that posts containing URLs are billed at a much higher rate than plain posts. No API endpoint exposes a dollar balance, so this rate is not observable from the command line — see `usage.md`. Check https://console.x.com before any high-volume posting run.

[!OUTPUT-SHAPE] Returns the API response with `data` containing the created post's `id` and `text`.
