import type { Client } from "@xdevplatform/xdk";

const DEFAULT_TWEET_FIELDS = [
  "author_id",
  "created_at",
  "conversation_id",
  "public_metrics",
  "text",
];

const DEFAULT_EXPANSIONS = ["author_id"];
const DEFAULT_USER_FIELDS = ["name", "username"];

interface Flags {
  ids: string[];
  tweetFields: string[];
  raw: boolean;
}

function parseFlags(args: string[]): Flags {
  if (args.length === 0 || args[0]?.startsWith("--")) {
    throw new Error("At least one post ID is required as the first argument.");
  }

  const flags: Flags = {
    ids: args[0].split(",").map((id) => id.trim()),
    tweetFields: DEFAULT_TWEET_FIELDS,
    raw: false,
  };

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--fields") {
      const value = args[++i];
      if (!value) throw new Error("--fields requires a comma-separated list");
      flags.tweetFields = value.split(",").map((f) => f.trim());
    } else if (arg === "--raw") {
      flags.raw = true;
    } else {
      throw new Error(`Unknown flag: ${arg}`);
    }
  }

  return flags;
}

export async function get(
  client: Client,
  args: string[],
): Promise<void> {
  const flags = parseFlags(args);

  const options = {
    tweetFields: flags.tweetFields,
    expansions: DEFAULT_EXPANSIONS,
    userFields: DEFAULT_USER_FIELDS,
  };

  if (flags.ids.length === 1) {
    const response = await client.posts.getById(flags.ids[0], options);
    if (flags.raw) {
      console.log(JSON.stringify(response, null, 2));
    } else {
      console.log(JSON.stringify(response.data, null, 2));
    }
  } else {
    const response = await client.posts.getByIds(flags.ids, options);
    if (flags.raw) {
      console.log(JSON.stringify(response, null, 2));
    } else {
      console.log(JSON.stringify(response.data ?? [], null, 2));
    }
  }
}
