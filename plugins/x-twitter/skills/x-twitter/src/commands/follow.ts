import { path, type Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { resolveMyId, resolveUserId } from "../lib/resolve.ts";

export async function follow(client: Client, args: string[]): Promise<unknown> {
  const { target } = parseArgs<{ target: string }>(args, {
    positional: { key: "target", label: "A username or user ID" },
  });

  const myId = await resolveMyId(client);
  const targetUserId = await resolveUserId(client, target);
  return client.post(path`/2/users/${myId}/following`, {
    target_user_id: targetUserId,
  });
}

export async function unfollow(
  client: Client,
  args: string[],
): Promise<unknown> {
  const { target } = parseArgs<{ target: string }>(args, {
    positional: { key: "target", label: "A username or user ID" },
  });

  const myId = await resolveMyId(client);
  const targetUserId = await resolveUserId(client, target);
  return client.delete(path`/2/users/${myId}/following/${targetUserId}`);
}
