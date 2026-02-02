export interface SearchFlags {
  query: string;
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

export function parseSearchFlags(args: string[]): SearchFlags {
  if (args.length === 0 || args[0]?.startsWith("--")) {
    throw new Error("A search query is required as the first argument.");
  }

  const flags: SearchFlags = {
    query: args[0],
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
