---
name: x-twitter
description: Interact with X (Twitter) API v2. Post tweets, search, engage, moderate, and analyze — all from your AI agent. Full 35-command skill for Twitter/X automation.
license: MIT
metadata:
  author: alberduris
  version: "1.9.2"
  tags: x, twitter, x-twitter, twitter-api, social-media, tweets, automation
allowed-tools: Bash(node *)
---

X (Twitter) API v2 skill using the authenticated user's own developer credentials (OAuth 1.0a, pay-per-use). All commands go through a single entry point: `node <base_directory>/x.ts <command> [flags]`, which Node.js 22.18 or later runs directly, with nothing to install or build. Each command has its own doc file with the full reference for flags and behavior.

[!COMMANDS]

Core:
a) `me` — authenticated user's own account data (profile, metrics, verification). @docs/me.md.
b) `search` — search posts by query. IMPORTANT: by default searches only the last 7 days; use `--all` (requires X_API_BEARER_TOKEN) for full archive. Do NOT use `search` with `conversation_id:` to read threads — use `thread` instead. @docs/search.md.
c) `get` — retrieve one or more posts by ID. @docs/get.md.
d) `post` — create a tweet, reply, or quote tweet. @docs/post.md.
e) `delete` — delete a post owned by the authenticated user. @docs/delete.md.
f) `thread` — retrieve a full thread/conversation given any tweet ID. Auto-resolves the conversation, paginates, and returns all tweets sorted chronologically. Use `--all` for threads older than 7 days. @docs/thread.md.

Engagement:
g) `like` — like a post by tweet ID. @docs/like.md.
h) `unlike` — remove a like from a post. @docs/like.md.
i) `repost` — repost (retweet) a post. @docs/repost.md.
j) `unrepost` — remove a repost. @docs/repost.md.

Social:
k) `user` — look up user(s) by username or ID. @docs/user.md.
l) `follow` — follow a user by username or ID. @docs/follow.md.
m) `unfollow` — unfollow a user. @docs/follow.md.
n) `followers` — list a user's followers. @docs/followers.md.
o) `following` — list accounts a user follows. @docs/followers.md.

Feed:
p) `timeline` — your home timeline (reverse chronological, not the algorithmic "For you" feed). Results skew heavily toward the authenticated account's own posts and do not reproduce the "Following" tab of the web client. Use `--exclude replies,retweets` to improve signal. @docs/timeline.md.
q) `mentions` — posts that mention you. @docs/mentions.md.

Bookmarks:
r) `bookmarks` — list your bookmarks. Adding or removing bookmarks is NOT possible: X accepts only OAuth 2.0 user context for those writes, which no supported credential provides. @docs/bookmark.md.

Moderation:
s) `mute` — mute a user. @docs/mute.md.
t) `unmute` — unmute a user. @docs/mute.md.
u) `muted` — list muted accounts. @docs/mute.md.
v) `blocked` — list blocked accounts. @docs/blocked.md.
w) `hide-reply` — hide a reply to your post. @docs/hide-reply.md.

Analytics:
x) `likers` — users who liked a post. @docs/likers.md.
y) `reposters` — users who reposted a post. @docs/reposters.md.
z) `quotes` — quote tweets of a post. @docs/quotes.md.
aa) `count` — count posts matching a query over time. @docs/count.md.
ab) `reposts-of-me` — reposts of your posts by others. @docs/reposts-of-me.md.

Discovery:
ac) `search-users` — search users by query. @docs/search-users.md.
ad) `trending` — trending topics (worldwide or personalized). @docs/trending.md.

Communities:
ae) `search-communities` — search communities by keyword (name, description). Returns metadata: name, description, member count, join policy. @docs/search-communities.md.
af) `community` — look up a community by ID. @docs/community.md.

News:
ag) `search-news` — search trending news stories by query. Returns headlines, summaries, categories, keywords, and related posts. @docs/search-news.md.
ah) `news` — look up a news story by ID. @docs/news.md.

Account:
ai) `usage` — posts read this cycle against the project cap. This is a READ QUOTA, not a credit balance: it cannot tell you whether you have money left, and it keeps working normally when credits are depleted. @docs/usage.md.

[!CREDENTIALS] Four OAuth 1.0a variables are REQUIRED: `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`. They resolve from the first source that provides them: a) `.env.local` in cwd, b) `.env` in cwd, c) `.env.local` in the skill directory (`<base_directory>`), d) `.env` in the skill directory, e) environment variables. `<base_directory>/.env.example` lists every variable. Obtain them from the X Developer Console (Apps > Keys and tokens). One CONDITIONALLY REQUIRED variable: `X_API_BEARER_TOKEN` (OAuth 2.0 App-Only Bearer Token), generated from the X Developer Console (Apps > Keys and tokens > Bearer Token). Five commands authenticate with it instead of OAuth 1.0a and fail without it, before sending any request: `count` (ALWAYS, not only with `--all`), `trending` (default worldwide branch; `--personalized` accepts only user context and does not need it), `search --all`, `thread --all`, and `usage`. Their endpoints (post counts, usage, trends by place, full-archive search) are App-Only. Every other command runs under OAuth 1.0a user context, which is what returns user-context fields such as `connection_status` and `receives_your_dm`.
