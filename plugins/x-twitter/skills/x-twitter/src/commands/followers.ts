import { path, type Client } from "../http/client.ts";
import { parseArgs, PAGINATION } from "../lib/args.ts";
import { USER_FIELDS } from "../lib/fields.ts";
import { resolveUserId } from "../lib/resolve.ts";
import { output, type Output } from "./output.ts";

interface ListFlags {
  target: string;
  maxResults?: number;
  nextToken?: string;
}

export async function followers(
  client: Client,
  args: string[],
): Promise<Output> {
  const flags = parseArgs<ListFlags>(args, {
    positional: { key: "target", label: "A username or user ID" },
    flags: { ...PAGINATION },
  });

  const userId = await resolveUserId(client, flags.target);

  const response = await client.get(path`/2/users/${userId}/followers`, {
    "user.fields": USER_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
  });
  return output(response, response.data ?? []);
}

export async function following(
  client: Client,
  args: string[],
): Promise<Output> {
  const flags = parseArgs<ListFlags>(args, {
    positional: { key: "target", label: "A username or user ID" },
    flags: { ...PAGINATION },
  });

  const userId = await resolveUserId(client, flags.target);

  const response = await client.get(path`/2/users/${userId}/following`, {
    "user.fields": USER_FIELDS,
    max_results: flags.maxResults,
    pagination_token: flags.nextToken,
  });
  return output(response, response.data ?? []);
}
