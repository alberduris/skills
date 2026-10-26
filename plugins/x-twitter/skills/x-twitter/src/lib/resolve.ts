import { path, type Client } from "../http/client.ts";

export async function resolveMyId(client: Client): Promise<string> {
  const response = await client.get("/2/users/me");
  const id = (response.data as { id?: string } | undefined)?.id;
  if (!id)
    throw new Error(
      "Could not resolve authenticated user ID from /2/users/me",
    );
  return id;
}

export async function resolveUserId(
  client: Client,
  input: string,
): Promise<string> {
  if (/^\d+$/.test(input)) return input;

  const username = input.startsWith("@") ? input.slice(1) : input;
  const response = await client.get(path`/2/users/by/username/${username}`);
  const id = (response.data as { id?: string } | undefined)?.id;
  if (!id) throw new Error(`Could not resolve user "${input}" to an ID.`);
  return id;
}
