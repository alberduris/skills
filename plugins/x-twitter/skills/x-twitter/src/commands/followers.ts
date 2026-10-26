import { path, type Client } from "../http/client.ts";
import { parseArgs, PAGINATION, RAW } from "../lib/args.ts";
import { USER_FIELDS } from "../lib/fields.ts";
import { resolveUserId } from "../lib/resolve.ts";

interface ListFlags {
  target: string;
  maxResults?: number;
  nextToken?: string;
  raw: boolean;
}

export async function followers(
  client: Client,
  args: string[],
): Promise<unknown> {
  const flags = parseArgs<ListFlags>(args, {
    positional: { key: "target", label: "A username or user ID" },
    flags: { ...PAGINATION, ...RAW },
  });

  const userId = await resolveUserId(client, flags.target);

  const response = await client.get(path`/2/users/${userId}/followers`, {
    "user.fields": USER_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
  });
  return flags.raw ? response : (response.data ?? []);
}

export async function following(
  client: Client,
  args: string[],
): Promise<unknown> {
  const flags = parseArgs<ListFlags>(args, {
    positional: { key: "target", label: "A username or user ID" },
    flags: { ...PAGINATION, ...RAW },
  });

  const userId = await resolveUserId(client, flags.target);

  const response = await client.get(path`/2/users/${userId}/following`, {
    "user.fields": USER_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
  });
  return flags.raw ? response : (response.data ?? []);
}
