# X API

31-command Claude Code skill for X/Twitter. Post, search, engage, moderate — all from your terminal.

## Commands

### Core
| Command | Description |
|---------|-------------|
| `me` | Your account data (profile, metrics, verification) |
| `search` | Search posts by query (recent or full archive) |
| `get` | Retrieve post(s) by ID |
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

### Bookmarks
| Command | Description |
|---------|-------------|
| `bookmark` | Bookmark a post |
| `unbookmark` | Remove a bookmark |
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

## Requirements

- Node.js 18+
- X Developer account with OAuth 1.0a credentials

## License

MIT
