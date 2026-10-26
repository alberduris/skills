import type { Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { POST_FIELDS } from "../posts/fields.ts";
import { hydrate, type Post } from "../posts/hydrate.ts";
import { output, type Output } from "./output.ts";

const WEEK_MS = 7 * 24 * 60 * 60 * 1000;

/**
 * The author's self-thread containing a post, as a human reads one on x.com:
 * the conversation's root plus the author's replies to themselves, oldest
 * first. Other people's replies are left out; `replies` reads those.
 */
export async function thread(client: Client, args: string[]): Promise<Output> {
  const flags = parseArgs<{ id: string; all: boolean }>(args, {
    positional: { key: "id", label: "A post ID from the thread" },
    flags: { "--all": { key: "all", type: "boolean" } },
  });

  const lookup = (id: string) => client.get("/2/tweets", { ids: id, ...POST_FIELDS });

  const seedResponse = await lookup(flags.id);
  const [seed] = hydrate(seedResponse);
  if (!seed) return output(seedResponse, []);

  const rootResponse =
    seed.conversation_id === seed.id ? seedResponse : await lookup(seed.conversation_id);
  const [root] = hydrate(rootResponse);
  if (!root) return output(rootResponse, []);

  const posts: Post[] = [root];
  const errors = [...(rootResponse.errors ?? [])];
  let nextToken: string | undefined;
  do {
    const page = await client.get(
      flags.all ? "/2/tweets/search/all" : "/2/tweets/search/recent",
      {
        query: `conversation_id:${root.id} from:${root.author.id}`,
        ...POST_FIELDS,
        max_results: 100,
        next_token: nextToken,
      },
    );
    posts.push(...hydrate(page).filter((post) => post.in_reply_to_user?.id === root.author.id));
    errors.push(...(page.errors ?? []));
    nextToken = page.meta?.next_token;
  } while (nextToken);

  // Oldest first by ID: IDs grow with creation time to the millisecond, while
  // created_at has whole seconds, which posts of a fast thread share.
  posts.sort((a, b) => (BigInt(a.id) < BigInt(b.id) ? -1 : 1));

  const hints: string[] = [];
  if (!flags.all && Date.now() - Date.parse(root.created_at) > WEEK_MS) {
    hints.push(
      `Recent search covers only the last 7 days and this thread began on ${root.created_at}, ` +
        "so any of its posts older than that are missing. Use --all to search the full archive.",
    );
  }
  // Judged by the thread's rule, not by absence from `posts`: recent search
  // also misses the author's own posts older than 7 days.
  const ownReply = seed.author.id === root.author.id && seed.in_reply_to_user?.id === root.author.id;
  if (seed.id !== root.id && !ownReply) {
    hints.push(`Post ${seed.id} is not part of @${root.author.username}'s thread; \`get ${seed.id}\` reads it.`);
  }
  return output(errors.length > 0 ? { errors } : {}, posts, hints);
}
