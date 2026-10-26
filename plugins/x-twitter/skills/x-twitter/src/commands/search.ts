import type { Client } from "../http/client.ts";
import { parseArgs, PAGINATION, TEMPORAL } from "../lib/args.ts";
import { resolveEnum } from "../lib/enums.ts";
import { POST_FIELDS } from "../posts/fields.ts";
import { hydrate } from "../posts/hydrate.ts";
import { output, type Output } from "./output.ts";

interface SearchFlags {
  query: string;
  all: boolean;
  maxResults?: number;
  sort?: string;
  startTime?: string;
  endTime?: string;
  sinceId?: string;
  untilId?: string;
  nextToken?: string;
}

const MIN_RESULTS = 10;

export async function search(client: Client, args: string[]): Promise<Output> {
  const flags = parseArgs<SearchFlags>(args, {
    positional: { key: "query", label: "A search query" },
    flags: {
      ...PAGINATION,
      ...TEMPORAL,
      "--all": { key: "all", type: "boolean" },
      "--sort": { key: "sort", type: "string" },
      "--since-id": { key: "sinceId", type: "string" },
      "--until-id": { key: "untilId", type: "string" },
    },
  });
  return searchPosts(client, flags);
}

/** One page of search results, recent or full-archive; `replies` shares it. */
export async function searchPosts(client: Client, flags: SearchFlags): Promise<Output> {
  const hints: string[] = [];
  let maxResults = flags.maxResults;
  if (maxResults !== undefined && maxResults < MIN_RESULTS) {
    hints.push(`--max-results was raised to ${MIN_RESULTS}, X's minimum. You requested ${maxResults}.`);
    maxResults = MIN_RESULTS;
  }

  const conversation = /conversation_id:(\d+)/.exec(flags.query);
  if (conversation) {
    hints.push(
      `To read the author's thread, use \`thread ${conversation[1]}\`; for the direct replies to a post, \`replies <id>\`.`,
    );
  }

  const response = await client.get(
    flags.all ? "/2/tweets/search/all" : "/2/tweets/search/recent",
    {
      query: flags.query,
      ...POST_FIELDS,
      max_results: maxResults,
      sort_order: flags.sort && resolveEnum("sort", flags.sort),
      start_time: flags.startTime,
      end_time: flags.endTime,
      since_id: flags.sinceId,
      until_id: flags.untilId,
      next_token: flags.nextToken,
    },
  );

  const posts = hydrate(response);
  if (!flags.all && posts.length === 0) {
    hints.push("Recent search covers only the last 7 days. Use --all to search the full archive.");
  }
  return output(response, posts, hints);
}
