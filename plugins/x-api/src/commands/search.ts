import type { Client } from "@xdevplatform/xdk";

interface SearchFlags {
  query: string;
  all: boolean;
  maxResults?: number;
  sortOrder?: "recency" | "relevancy";
  startTime?: string;
  endTime?: string;
  sinceId?: string;
  untilId?: string;
  nextToken?: string;
  tweetFields: string[];
  raw: boolean;
}

const DEFAULT_TWEET_FIELDS = [
  "author_id",
  "created_at",
  "conversation_id",
  "public_metrics",
  "text",
];

const DEFAULT_EXPANSIONS = ["author_id"];
const DEFAULT_USER_FIELDS = ["name", "username"];

function parseFlags(args: string[]): SearchFlags {
  if (args.length === 0 || args[0]?.startsWith("--")) {
    throw new Error("A search query is required as the first argument.");
  }

  const flags: SearchFlags = {
    query: args[0],
    all: false,
    tweetFields: DEFAULT_TWEET_FIELDS,
    raw: false,
  };

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    const next = (): string => {
      const v = args[++i];
      if (!v) throw new Error(`${arg} requires a value`);
      return v;
    };

    switch (arg) {
      case "--all":
        flags.all = true;
        break;
      case "--max-results":
        flags.maxResults = Number(next());
        break;
      case "--sort":
        flags.sortOrder = next() as "recency" | "relevancy";
        break;
      case "--start-time":
        flags.startTime = next();
        break;
      case "--end-time":
        flags.endTime = next();
        break;
      case "--since-id":
        flags.sinceId = next();
        break;
      case "--until-id":
        flags.untilId = next();
        break;
      case "--next-token":
        flags.nextToken = next();
        break;
      case "--fields":
        flags.tweetFields = next().split(",").map((f) => f.trim());
        break;
      case "--raw":
        flags.raw = true;
        break;
      default:
        throw new Error(`Unknown flag: ${arg}`);
    }
  }

  return flags;
}

export async function search(
  client: Client,
  args: string[],
): Promise<void> {
  const flags = parseFlags(args);

  const options = {
    tweetFields: flags.tweetFields,
    expansions: DEFAULT_EXPANSIONS,
    userFields: DEFAULT_USER_FIELDS,
    ...(flags.maxResults && { maxResults: flags.maxResults }),
    ...(flags.sortOrder && { sortOrder: flags.sortOrder }),
    ...(flags.startTime && { startTime: flags.startTime }),
    ...(flags.endTime && { endTime: flags.endTime }),
    ...(flags.sinceId && { sinceId: flags.sinceId }),
    ...(flags.untilId && { untilId: flags.untilId }),
    ...(flags.nextToken && { nextToken: flags.nextToken }),
  };

  const response = flags.all
    ? await client.posts.searchAll(flags.query, options)
    : await client.posts.searchRecent(flags.query, options);

  if (flags.raw) {
    console.log(JSON.stringify(response, null, 2));
  } else {
    console.log(JSON.stringify(response.data ?? [], null, 2));
  }
}
