import type { Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { POST_FIELDS } from "../posts/fields.ts";
import { hydrate, type Post } from "../posts/hydrate.ts";
import { output, type Output } from "./output.ts";

const WEEK_MS = 7 * 24 * 60 * 60 * 1000;

/**
 * The author's thread containing a post, as a human reads one on x.com: the
 * conversation's root plus the author's replies to it or to another post
 * already in the thread, oldest first. Other people's replies, and the
 * author's replies under them, are left out; `replies` reads those.
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

  const found: Post[] = [];
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
    found.push(...hydrate(page));
    errors.push(...(page.errors ?? []));
    nextToken = page.meta?.next_token;
  } while (nextToken);

  // Oldest first by ID: IDs grow with creation time to the millisecond, while
  // created_at has whole seconds, which posts of a fast thread share. A reply's
  // ID is larger than its parent's, so one pass in this order builds the chain.
  found.sort((a, b) => (BigInt(a.id) < BigInt(b.id) ? -1 : 1));
  const chain = new Map([[root.id, root]]);
  for (const post of found) {
    const parent = post.referenced_tweets?.find((ref) => ref.type === "replied_to")?.id;
    if (parent && chain.has(parent)) chain.set(post.id, post);
  }

  const hints: string[] = [];
  if (!flags.all && Date.now() - Date.parse(root.created_at) > WEEK_MS) {
    hints.push(
      `Recent search covers only the last 7 days and this thread began on ${root.created_at}, ` +
        "so any of its posts older than that are missing, along with the posts that follow them. " +
        "Use --all to search the full archive.",
    );
  } else if (!chain.has(seed.id)) {
    // Claimed only when the search covered the whole conversation: a missing
    // older post breaks the chain and would drop a given post that belongs.
    hints.push(`Post ${seed.id} is not part of @${root.author.username}'s thread; \`get ${seed.id}\` reads it.`);
  }
  return output(errors.length > 0 ? { errors } : {}, [...chain.values()], hints);
}
