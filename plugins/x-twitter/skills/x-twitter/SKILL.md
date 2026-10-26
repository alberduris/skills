---
name: x-twitter
description: Interact with X (Twitter) API v2. Post tweets, search, engage, moderate, and analyze — all from your AI agent. Full 36-command skill for Twitter/X automation.
license: MIT
metadata:
  author: alberduris
  version: "2.0.0"
  tags: x, twitter, x-twitter, twitter-api, social-media, tweets, automation
allowed-tools: Bash(node *)
---

X (Twitter) API v2 skill using the authenticated user's own developer credentials (OAuth 1.0a, pay-per-use). All commands go through a single entry point: `node <base_directory>/x.ts <command> [flags]`, which Node.js 22.18 or later runs directly, with nothing to install or build. Each command has its own doc file with the full reference for flags and behavior.

[!OUTPUT] Every command prints one JSON object: X's response with `includes` folded into `data`, plus our hints, as `{ data, meta?, errors?, hints? }`. `meta` and `errors` are exactly as X sent them: `meta.next_token` is the value for `--next-token`, and `errors` says why something is missing, including partial errors next to good data. `hints` is an array of strings from the CLI. `data` is absent only when X sent none. Field names are X's own.

[!POSTS] Every command that returns posts (`get`, `search`, `thread`, `replies`, `quotes`, `mentions`, `timeline`, `bookmarks`, `reposts-of-me`, `me --pinned-tweet`) shows them as x.com does, in one shape: `author` (id, name, username) in place of `author_id`; `text` is the full text a human reads, long posts included, with t.co links expanded and the links to the post's own media and to the quoted post removed; `media` holds the attached photos and videos as X describes them (type, url, preview_image_url, duration_ms, variants, alt_text); `referenced_tweets` embeds quoted and retweeted posts in full, while a replied-to post stays `{ type: "replied_to", id }` and the replied-to user is in `in_reply_to_user`; `article` holds an X Article's `title` and full `plain_text`. A referenced post X did not return stays as its `{ type, id }`, and `errors` says why.

[!COMMANDS]

Core:
a) `me` — authenticated user's own account data (profile, metrics, verification). @docs/me.md.
b) `search` — search posts by query. IMPORTANT: by default searches only the last 7 days; use `--all` for the full archive. Do NOT use `search` with `conversation_id:` to read threads or replies — use `thread` or `replies` instead. @docs/search.md.
c) `get` — retrieve one or more posts by ID; `data` is always an array. @docs/get.md.
d) `post` — create a tweet, reply, or quote tweet. @docs/post.md.
e) `delete` — delete a post owned by the authenticated user. @docs/delete.md.
f) `thread` — the author's thread containing a post: the first post plus the author's replies to themselves, oldest first. Other people's replies are left out. Use `--all` for threads older than 7 days. @docs/thread.md.
g) `replies` — the direct replies to a post, one page at a time. @docs/replies.md.

Engagement:
h) `like` — like a post by tweet ID. @docs/like.md.
i) `unlike` — remove a like from a post. @docs/like.md.
j) `repost` — repost (retweet) a post. @docs/repost.md.
k) `unrepost` — remove a repost. @docs/repost.md.

Social:
l) `user` — look up user(s) by username or ID. @docs/user.md.
m) `follow` — follow a user by username or ID. @docs/follow.md.
n) `unfollow` — unfollow a user. @docs/follow.md.
o) `followers` — list a user's followers. @docs/followers.md.
p) `following` — list accounts a user follows. @docs/followers.md.

Feed:
q) `timeline` — your home timeline (reverse chronological, not the algorithmic "For you" feed). Results skew heavily toward the authenticated account's own posts and do not reproduce the "Following" tab of the web client. Use `--exclude replies,retweets` to improve signal. @docs/timeline.md.
r) `mentions` — posts that mention you. @docs/mentions.md.

Bookmarks:
s) `bookmarks` — list your bookmarks. Adding or removing bookmarks is NOT possible: X accepts only OAuth 2.0 user context for those writes, which no supported credential provides. @docs/bookmark.md.

Moderation:
t) `mute` — mute a user. @docs/mute.md.
u) `unmute` — unmute a user. @docs/mute.md.
v) `muted` — list muted accounts. @docs/mute.md.
w) `blocked` — list blocked accounts. @docs/blocked.md.
x) `hide-reply` — hide a reply to your post. @docs/hide-reply.md.

Analytics:
y) `likers` — users who liked a post. @docs/likers.md.
z) `reposters` — users who reposted a post. @docs/reposters.md.
aa) `quotes` — quote tweets of a post. @docs/quotes.md.
ab) `count` — count posts matching a query over time. @docs/count.md.
ac) `reposts-of-me` — reposts of your posts by others. @docs/reposts-of-me.md.

Discovery:
ad) `search-users` — search users by query. @docs/search-users.md.
ae) `trending` — trending topics (worldwide or personalized). @docs/trending.md.

Communities:
af) `search-communities` — search communities by keyword (name, description). Returns metadata: name, description, member count, join policy. @docs/search-communities.md.
ag) `community` — look up a community by ID. @docs/community.md.

News:
ah) `search-news` — search trending news stories by query. Returns headlines, summaries, categories, keywords, and related posts. @docs/search-news.md.
ai) `news` — look up a news story by ID. @docs/news.md.

Account:
aj) `usage` — posts read this cycle against the project cap. This is a READ QUOTA, not a credit balance: it cannot tell you whether you have money left, and it keeps working normally when credits are depleted. @docs/usage.md.

[!CREDENTIALS] Four OAuth 1.0a variables are REQUIRED: `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`. They resolve from the first source that provides them: a) `.env.local` in cwd, b) `.env` in cwd, c) `.env.local` in the skill directory (`<base_directory>`), d) `.env` in the skill directory, e) environment variables. `<base_directory>/.env.example` lists every variable. Obtain them from the X Developer Console (Apps > Keys and tokens). One CONDITIONALLY REQUIRED variable: `X_API_BEARER_TOKEN` (OAuth 2.0 App-Only Bearer Token), generated from the X Developer Console (Apps > Keys and tokens > Bearer Token). Three commands authenticate with it instead of OAuth 1.0a and fail without it, before sending any request: `count` (ALWAYS, not only with `--all`), `trending` (default worldwide branch; `--personalized` accepts only user context and does not need it), and `usage`. Their endpoints (post counts, usage, trends by place) are App-Only. Every other command, full-archive search included (`search --all`, `thread --all`, `replies --all`), runs under OAuth 1.0a user context, which is what returns user-context fields such as `connection_status` and `receives_your_dm`.
