import type { Client } from "../http/client.ts";
import { parseArgs, PAGINATION, TEMPORAL, RAW } from "../lib/args.ts";
import { TWEET_FIELDS, TWEET_EXPANSIONS, TWEET_USER_FIELDS } from "../lib/fields.ts";
import { resolveEnum } from "../lib/enums.ts";

interface SearchFlags {
  query: string;
  all: boolean;
  maxResults?: number;
  sortOrder?: string;
  startTime?: string;
  endTime?: string;
  sinceId?: string;
  untilId?: string;
  nextToken?: string;
  tweetFields: string[];
  raw: boolean;
}

export async function search(
  client: Client,
  args: string[],
): Promise<unknown> {
  const flags = parseArgs<SearchFlags>(args, {
    positional: { key: "query", label: "A search query" },
    flags: {
      ...PAGINATION,
      ...TEMPORAL,
      ...RAW,
      "--all": { key: "all", type: "boolean" },
      "--sort": { key: "sortOrder", type: "string" },
      "--since-id": { key: "sinceId", type: "string" },
      "--until-id": { key: "untilId", type: "string" },
      "--fields": { key: "tweetFields", type: "string[]" },
    },
    defaults: { tweetFields: TWEET_FIELDS },
  });

  const MIN_RESULTS = 10;
  const hints: string[] = [];
  if (flags.maxResults !== undefined && flags.maxResults < MIN_RESULTS) {
    hints.push(`Hint: maxResults was raised to ${MIN_RESULTS} (Twitter API minimum). You requested ${flags.maxResults}.`);
    flags.maxResults = MIN_RESULTS;
  }

  // Nudge: conversation_id: in search query → suggest thread command
  if (/conversation_id:\d+/.test(flags.query)) {
    const match = flags.query.match(/conversation_id:(\d+)/);
    hints.push(`Hint: to read a full thread, use the \`thread\` command instead: \`thread ${match?.[1] ?? "<tweet_id>"}\`. It auto-resolves the conversation, paginates, and sorts chronologically.`);
  }

  if (flags.sortOrder !== undefined) {
    flags.sortOrder = resolveEnum("sortOrder", flags.sortOrder);
  }

  const query = {
    query: flags.query,
    "tweet.fields": flags.tweetFields,
    expansions: TWEET_EXPANSIONS,
    "user.fields": TWEET_USER_FIELDS,
    max_results: flags.maxResults,
    sort_order: flags.sortOrder,
    start_time: flags.startTime,
    end_time: flags.endTime,
    since_id: flags.sinceId,
    until_id: flags.untilId,
    next_token: flags.nextToken,
  };

  // The full archive accepts only app-only auth
  const response = flags.all
    ? await client.get("/2/tweets/search/all", query, "app-only")
    : await client.get("/2/tweets/search/recent", query);

  const data = flags.raw ? response : (response.data ?? []);

  // Nudge: empty results on recent search → 7-day limitation
  if (!flags.all && Array.isArray(data) && data.length === 0) {
    hints.push("Hint: recent search only covers the last 7 days. Use --all (requires X_API_BEARER_TOKEN) to search the full archive.");
  }

  if (hints.length) return { hint: hints.join(" "), data };
  return data;
}
