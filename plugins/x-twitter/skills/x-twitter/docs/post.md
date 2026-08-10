Creates a new post (tweet, reply, or quote tweet). Maps to POST /2/tweets. Invoke via `node <base_directory>/x.js post "<text>" [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — creates a standalone tweet with the given text. b) `--reply-to <id>` — makes this post a reply to the specified post ID. c) `--quote <id>` — makes this a quote tweet of the specified post ID. d) `--reply-settings <following|mentionedUsers|subscribers|verified>` — restrict who can reply. e) `--paid-partnership` — labels the post as paid promotion. Verified end-to-end: the created post reads back with `paidPartnership: true`.

[!THREADS] To create a thread, post the first tweet, capture its ID from the response, then use `--reply-to <id>` for each subsequent tweet in the chain.

[!REPLY-LIMITS] X's changelog (2026-02-23) states that programmatic replies are only permitted when the original post's author has "summoned" the replier, by @mentioning that account or quoting one of its posts. This is UNVERIFIED by us: replying inside a conversation the authenticated user already participates in does work, but the restricted case — replying to an unrelated third party — was never tested. Treat it as reported-by-X, not confirmed; two other changelog claims from the same period (removal of like/follow/quote writes, and retweets disappearing from search results) were tested and proved false.

[!COST] Replying to or quoting a post inserts a `t.co` URL into the post text. X announced (2026-04-16) that posts containing URLs are billed at a much higher rate than plain posts, but the API exposes no dollar balance, so we could not measure it — see `usage.md`. Verify against https://console.x.com before running any high-volume posting.

[!OUTPUT-SHAPE] Returns the API response with `data` containing the created post's `id` and `text`.
