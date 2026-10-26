import type { Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { resolveEnum } from "../lib/enums.ts";

interface PostFlags {
  text: string;
  replyTo?: string;
  quoteTweetId?: string;
  replySettings?: string;
  paidPartnership: boolean;
}

export async function post(
  client: Client,
  args: string[],
): Promise<unknown> {
  const flags = parseArgs<PostFlags>(args, {
    positional: { key: "text", label: "Post text" },
    flags: {
      "--reply-to": { key: "replyTo", type: "string" },
      "--quote": { key: "quoteTweetId", type: "string" },
      "--reply-settings": { key: "replySettings", type: "string" },
      "--paid-partnership": { key: "paidPartnership", type: "boolean" },
    },
  });

  if (flags.replySettings) {
    flags.replySettings = resolveEnum("replySettings", flags.replySettings);
  }

  const body: Record<string, unknown> = { text: flags.text };

  if (flags.replyTo) {
    body.reply = { in_reply_to_tweet_id: flags.replyTo };
  }
  if (flags.quoteTweetId) {
    body.quote_tweet_id = flags.quoteTweetId;
  }
  if (flags.replySettings) {
    body.reply_settings = flags.replySettings;
  }
  if (flags.paidPartnership) {
    body.paid_partnership = true;
  }

  return client.post("/2/tweets", body);
}
