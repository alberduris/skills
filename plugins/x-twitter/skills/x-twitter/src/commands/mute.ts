import { path, type Client } from "../http/client.ts";
import { parseArgs, PAGINATION } from "../lib/args.ts";
import { USER_FIELDS } from "../lib/fields.ts";
import { resolveMyId, resolveUserId } from "../lib/resolve.ts";
import { output, type Output } from "./output.ts";

export async function mute(client: Client, args: string[]): Promise<Output> {
  const { target } = parseArgs<{ target: string }>(args, {
    positional: { key: "target", label: "A username or user ID" },
  });

  const myId = await resolveMyId(client);
  const targetUserId = await resolveUserId(client, target);
  const response = await client.post(path`/2/users/${myId}/muting`, {
    target_user_id: targetUserId,
  });
  return output(response);
}

export async function unmute(client: Client, args: string[]): Promise<Output> {
  const { target } = parseArgs<{ target: string }>(args, {
    positional: { key: "target", label: "A username or user ID" },
  });

  const myId = await resolveMyId(client);
  const targetUserId = await resolveUserId(client, target);
  return output(await client.delete(path`/2/users/${myId}/muting/${targetUserId}`));
}

export async function muted(client: Client, args: string[]): Promise<Output> {
  const flags = parseArgs<{
    maxResults?: number;
    nextToken?: string;
  }>(args, { flags: { ...PAGINATION } });

  const myId = await resolveMyId(client);

  const response = await client.get(path`/2/users/${myId}/muting`, {
    "user.fields": USER_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
  });
  return output(response, response.data ?? []);
}
