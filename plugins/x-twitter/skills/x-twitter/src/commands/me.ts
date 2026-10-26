import type { Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { USER_FIELDS_EXTENDED } from "../lib/fields.ts";
import { POST_FIELDS } from "../posts/fields.ts";
import { hydrate } from "../posts/hydrate.ts";
import { output, type Output } from "./output.ts";

interface MeFlags {
  fields: string[];
  pinnedTweet: boolean;
}

export async function me(client: Client, args: string[]): Promise<Output> {
  const flags = parseArgs<MeFlags>(args, {
    flags: {
      "--fields": { key: "fields", type: "string[]" },
      "--pinned-tweet": { key: "pinnedTweet", type: "boolean" },
    },
    defaults: { fields: USER_FIELDS_EXTENDED },
  });

  const response = await client.get("/2/users/me", {
    "user.fields": flags.pinnedTweet ? [...flags.fields, "pinned_tweet_id"] : flags.fields,
  });
  const { pinned_tweet_id, ...user } = (response.data ?? {}) as { pinned_tweet_id?: string };
  if (!flags.pinnedTweet || !pinned_tweet_id) return output(response);

  // X's pinned_tweet_id expansion answers "Not Found" for pinned posts that
  // exist (seen on public accounts), so the post is looked up like any other.
  const pinned = await client.get("/2/tweets", { ids: pinned_tweet_id, ...POST_FIELDS });
  const [post] = hydrate(pinned);
  return output(
    { errors: pinned.errors },
    post ? { ...user, pinned_tweet: post } : response.data,
  );
}
