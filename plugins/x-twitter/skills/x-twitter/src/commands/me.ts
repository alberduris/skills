import type { Client } from "../http/client.ts";
import { parseArgs, RAW } from "../lib/args.ts";
import { USER_FIELDS_EXTENDED } from "../lib/fields.ts";

interface MeFlags {
  fields: string[];
  pinnedTweet: boolean;
  raw: boolean;
}

export async function me(client: Client, args: string[]): Promise<unknown> {
  const flags = parseArgs<MeFlags>(args, {
    flags: {
      ...RAW,
      "--fields": { key: "fields", type: "string[]" },
      "--pinned-tweet": { key: "pinnedTweet", type: "boolean" },
    },
    defaults: { fields: USER_FIELDS_EXTENDED },
  });

  const response = await client.get("/2/users/me", {
    "user.fields": flags.fields,
    ...(flags.pinnedTweet && {
      expansions: "pinned_tweet_id",
      "tweet.fields": ["created_at", "text", "public_metrics"],
    }),
  });

  if (flags.raw || flags.pinnedTweet) {
    return response;
  }
  return response.data;
}
