import type { Client } from "@xdevplatform/xdk";
import { parseArgs, RAW } from "../lib/args.js";
import { TWEET_FIELDS, TWEET_EXPANSIONS, TWEET_USER_FIELDS } from "../lib/fields.js";

interface ThreadFlags {
  tweetId: string;
  all: boolean;
  raw: boolean;
}

export async function thread(
  client: Client,
  args: string[],
): Promise<unknown> {
  const flags = parseArgs<ThreadFlags>(args, {
    positional: { key: "tweetId", label: "A tweet ID from the thread" },
    flags: {
      ...RAW,
      "--all": { key: "all", type: "boolean" },
    },
  });

  const options = {
    tweetFields: TWEET_FIELDS,
    expansions: TWEET_EXPANSIONS,
    userFields: TWEET_USER_FIELDS,
  };

  // 1. Fetch the given tweet to obtain its conversation_id
  const seedResponse = await client.posts.getById(flags.tweetId, options);
  const seedTweet = seedResponse.data as Record<string, unknown> | undefined;
  if (!seedTweet) {
    return { error: `Tweet ${flags.tweetId} not found.` };
  }

  const conversationId = (seedTweet.conversation_id as string) ?? flags.tweetId;

  // 2. Search all tweets in the conversation (auto-paginate)
  const query = `conversation_id:${conversationId}`;
  const seen = new Set<string>();
  const tweets: Record<string, unknown>[] = [];
  let nextToken: string | undefined;

  do {
    const searchOpts = {
      ...options,
      maxResults: 100,
      ...(nextToken && { nextToken }),
    };

    const response = flags.all
      ? await client.posts.searchAll(query, searchOpts)
      : await client.posts.searchRecent(query, searchOpts);

    const data = response.data as Record<string, unknown>[] | undefined;
    if (data) {
      for (const tweet of data) {
        const id = tweet.id as string;
        if (!seen.has(id)) {
          seen.add(id);
          tweets.push(tweet);
        }
      }
    }

    nextToken = (response.meta as { next_token?: string } | undefined)?.next_token;
  } while (nextToken);

  // 3. Ensure root tweet is included (search may miss it if older than 7 days)
  if (!seen.has(conversationId)) {
    if (conversationId === flags.tweetId) {
      tweets.unshift(seedTweet);
    } else {
      const rootResponse = await client.posts.getById(conversationId, options);
      const rootTweet = rootResponse.data as Record<string, unknown> | undefined;
      if (rootTweet) tweets.unshift(rootTweet);
    }
  }

  // 4. Ensure the seed tweet itself is included (may be outside 7-day window)
  if (!seen.has(flags.tweetId) && flags.tweetId !== conversationId) {
    tweets.push(seedTweet);
  }

  // 5. Sort chronologically
  tweets.sort((a, b) => {
    const ta = new Date((a.created_at as string) ?? "0").getTime();
    const tb = new Date((b.created_at as string) ?? "0").getTime();
    return ta - tb;
  });

  // 6. Hint if recent search likely missed tweets
  const hints: string[] = [];
  if (!flags.all && tweets.length <= 1) {
    hints.push(
      "Hint: recent search only covers the last 7 days. If this thread is older, use --all (requires X_API_BEARER_TOKEN).",
    );
  }

  if (hints.length || flags.raw) {
    return { ...(hints.length && { hint: hints.join(" ") }), data: tweets };
  }
  return tweets;
}
