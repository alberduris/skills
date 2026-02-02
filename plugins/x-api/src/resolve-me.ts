import type { Client } from "@xdevplatform/xdk";

let cachedId: string | null = null;

export async function resolveMyId(client: Client): Promise<string> {
  if (cachedId) return cachedId;
  const response = await client.users.getMe();
  const id = response.data?.id;
  if (!id) throw new Error("Could not resolve authenticated user ID from /2/users/me");
  cachedId = id;
  return id;
}
