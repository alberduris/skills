import { path, type Client } from "../http/client.ts";
import { parseArgs, PAGINATION, RAW } from "../lib/args.ts";
import { USER_FIELDS } from "../lib/fields.ts";
import { resolveMyId, resolveUserId } from "../lib/resolve.ts";

export async function mute(client: Client, args: string[]): Promise<unknown> {
  const { target } = parseArgs<{ target: string }>(args, {
    positional: { key: "target", label: "A username or user ID" },
  });

  const myId = await resolveMyId(client);
  const targetUserId = await resolveUserId(client, target);
  return client.post(path`/2/users/${myId}/muting`, {
    target_user_id: targetUserId,
  });
}

export async function unmute(client: Client, args: string[]): Promise<unknown> {
  const { target } = parseArgs<{ target: string }>(args, {
    positional: { key: "target", label: "A username or user ID" },
  });

  const myId = await resolveMyId(client);
  const targetUserId = await resolveUserId(client, target);
  return client.delete(path`/2/users/${myId}/muting/${targetUserId}`);
}

export async function muted(client: Client, args: string[]): Promise<unknown> {
  const flags = parseArgs<{
    maxResults?: number;
    nextToken?: string;
    raw: boolean;
  }>(args, { flags: { ...PAGINATION, ...RAW } });

  const myId = await resolveMyId(client);

  const response = await client.get(path`/2/users/${myId}/muting`, {
    "user.fields": USER_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
  });
  return flags.raw ? response : (response.data ?? []);
}
