import type { Client } from "@xdevplatform/xdk";
import { parseArgs } from "../lib/args.js";
import { resolveEnum } from "../lib/enums.js";

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
    body.reply = { inReplyToTweetId: flags.replyTo };
  }
  if (flags.quoteTweetId) {
    body.quoteTweetId = flags.quoteTweetId;
  }
  if (flags.replySettings) {
    body.replySettings = flags.replySettings;
  }
  if (flags.paidPartnership) {
    body.paidPartnership = true;
  }

  return client.posts.create(body);
}
