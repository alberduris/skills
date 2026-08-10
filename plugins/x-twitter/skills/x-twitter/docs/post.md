Creates a new post (tweet, reply, or quote tweet). Maps to POST /2/tweets. Invoke via `node <base_directory>/x.js post "<text>" [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — creates a standalone tweet with the given text. b) `--reply-to <id>` — makes this post a reply to the specified post ID. c) `--quote <id>` — makes this a quote tweet of the specified post ID. d) `--reply-settings <following|mentionedUsers|subscribers|verified>` — restrict who can reply. e) `--paid-partnership` — labels the post as paid promotion; the created post reads back with `paidPartnership: true`.

[!THREADS] To create a thread, post the first tweet, capture its ID from the response, then use `--reply-to <id>` for each subsequent tweet in the chain.

[!REPLY-LIMITS] Replying to an account that has never @mentioned or quoted the authenticated account may be rejected. Replying inside a conversation the authenticated account already participates in works. Treat the restricted case as unproven: exercise it once against an account you control before depending on it.

[!COST] Replying to or quoting a post inserts a `t.co` URL into the post text. Posts containing URLs may be billed at a higher rate than plain-text posts. No endpoint exposes a dollar balance, so the rate is not observable from the command line — see `usage.md`. Check the Developer Console at https://console.x.com before any high-volume posting run.

[!OUTPUT-SHAPE] Returns the API response with `data` containing the created post's `id` and `text`.
