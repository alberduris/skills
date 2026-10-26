import { path, type Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { resolveMyId, resolveUserId } from "../lib/resolve.ts";
import { output, type Output } from "./output.ts";

export async function follow(client: Client, args: string[]): Promise<Output> {
  const { target } = parseArgs<{ target: string }>(args, {
    positional: { key: "target", label: "A username or user ID" },
  });

  const myId = await resolveMyId(client);
  const targetUserId = await resolveUserId(client, target);
  const response = await client.post(path`/2/users/${myId}/following`, {
    target_user_id: targetUserId,
  });
  return output(response);
}

export async function unfollow(
  client: Client,
  args: string[],
): Promise<Output> {
  const { target } = parseArgs<{ target: string }>(args, {
    positional: { key: "target", label: "A username or user ID" },
  });

  const myId = await resolveMyId(client);
  const targetUserId = await resolveUserId(client, target);
  return output(await client.delete(path`/2/users/${myId}/following/${targetUserId}`));
}
