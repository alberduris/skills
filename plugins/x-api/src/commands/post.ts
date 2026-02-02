import type { Client } from "@xdevplatform/xdk";

interface Flags {
  text: string;
  replyTo?: string;
  quoteTweetId?: string;
  replySettings?: "following" | "mentionedUsers" | "subscribers" | "verified";
}

function parseFlags(args: string[]): Flags {
  if (args.length === 0 || args[0]?.startsWith("--")) {
    throw new Error("Post text is required as the first argument.");
  }

  const flags: Flags = { text: args[0] };

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    const next = (): string => {
      const v = args[++i];
      if (!v) throw new Error(`${arg} requires a value`);
      return v;
    };

    switch (arg) {
      case "--reply-to":
        flags.replyTo = next();
        break;
      case "--quote":
        flags.quoteTweetId = next();
        break;
      case "--reply-settings":
        flags.replySettings = next() as Flags["replySettings"];
        break;
      default:
        throw new Error(`Unknown flag: ${arg}`);
    }
  }

  return flags;
}

export async function post(
  client: Client,
  args: string[],
): Promise<void> {
  const flags = parseFlags(args);

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

  const response = await client.posts.create(body);
  console.log(JSON.stringify(response, null, 2));
}
