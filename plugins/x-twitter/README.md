# X API

37-command Claude Code skill for X/Twitter. Post, search, engage, moderate — all from your terminal.

## Commands

### Core
| Command | Description |
|---------|-------------|
| `me` | Your account data (profile, metrics, verification) |
| `search` | Search posts by query (recent or full archive) |
| `get` | Retrieve post(s) by ID |
| `thread` | Retrieve a full thread/conversation by any tweet ID |
| `post` | Create a tweet, reply, or quote tweet |
| `delete` | Delete a post |

### Engagement
| Command | Description |
|---------|-------------|
| `like` | Like a post |
| `unlike` | Remove a like |
| `repost` | Repost (retweet) a post |
| `unrepost` | Remove a repost |

### Social
| Command | Description |
|---------|-------------|
| `user` | Look up user(s) by username or ID |
| `follow` | Follow a user |
| `unfollow` | Unfollow a user |
| `followers` | List a user's followers |
| `following` | List accounts a user follows |

### Feed
| Command | Description |
|---------|-------------|
| `timeline` | Your home timeline |
| `mentions` | Posts that mention you |

> **Note (2026-02-14):** The `timeline` command returns the reverse chronological timeline, not the algorithmic "For you" feed. Even so, the X API returns heavily skewed results — mostly own tweets — and does not faithfully reproduce the "Following" tab on x.com. Use `--exclude replies,retweets` to filter out own replies and retweets and get a slightly better signal.

### Bookmarks
| Command | Description |
|---------|-------------|
| `bookmark` | Bookmark a post (unavailable: needs OAuth 2.0 user context) |
| `unbookmark` | Remove a bookmark (unavailable: needs OAuth 2.0 user context) |
| `bookmarks` | List your bookmarks |

### Moderation
| Command | Description |
|---------|-------------|
| `mute` | Mute a user |
| `unmute` | Unmute a user |
| `muted` | List muted accounts |
| `blocked` | List blocked accounts |
| `hide-reply` | Hide a reply to your post |

### Analytics
| Command | Description |
|---------|-------------|
| `likers` | Users who liked a post |
| `reposters` | Users who reposted a post |
| `quotes` | Quote tweets of a post |
| `count` | Count posts matching a query over time |
| `reposts-of-me` | Reposts of your posts by others |

### Discovery
| Command | Description |
|---------|-------------|
| `search-users` | Search users by query |
| `trending` | Trending topics (worldwide or personalized) |

### Communities
| Command | Description |
|---------|-------------|
| `search-communities` | Search communities by keyword |
| `community` | Look up a community by ID |

### News
| Command | Description |
|---------|-------------|
| `search-news` | Search news stories by query |
| `news` | Look up a news story by ID |

### Account
| Command | Description |
|---------|-------------|
| `usage` | Posts read this cycle against the project cap (a read quota, not a credit balance) |

## Setup

1. Go to [console.x.com](https://console.x.com) > Apps > Create a new App
2. Enable OAuth 1.0a with **Read and Write** permissions
3. Go to Keys and tokens, generate all four credentials
4. Add them to `.env.local` or `.env`:

```
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### Optional: Bearer Token

`count`, `trending` (worldwide; `--personalized` runs without it), `usage`, and `search`/`thread` with `--all` (full archive back to 2006) accept only an App-Only Bearer Token:

```
X_API_BEARER_TOKEN=your_bearer_token
```

Generate it from the X Developer Console under **Keys and tokens > Bearer Token**. The CLI attaches it to those commands only; every other command runs under your OAuth 1.0a user context, so user-context fields such as `connection_status` stay in the responses.

## Requirements

- Node.js 18+
- X Developer account with OAuth 1.0a credentials
- (Optional) Bearer Token for `count`, worldwide `trending`, `usage` and full archive search

## License

MIT
