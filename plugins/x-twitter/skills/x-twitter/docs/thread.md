Retrieves the author's thread containing a post, as a human reads one on x.com: the conversation's first post plus every post in it where the author replies to themselves, oldest first. Other people's replies, and the author's replies to them, are left out; use `replies` for those. Pass any post ID from the thread. Invoke via `node <base_directory>/x.ts thread <tweet_id> [flags]`. Output is JSON to stdout.

[!HOW-IT-WORKS] 1) Looks up the given post to find its conversation (the conversation's ID is its first post's ID) and, if different, looks up that first post to find the author. 2) Searches `conversation_id:<id> from:<author>`, following every page. 3) Keeps the posts whose `in_reply_to_user` is the author.

[!FLAGS] a) no flags — searches the last 7 days. b) `--all` — searches the full archive. Use it for threads older than 7 days; `hints` says when the thread began before that window.

[!OUTPUT-SHAPE] `data` is an array of posts, oldest first. When the given post does not exist, `data` is empty and `errors` says why.

[!COST] Every post returned is a billed read. Only the author's posts are fetched, so a thread with hundreds of replies from others costs about as many reads as the author's own posts.
