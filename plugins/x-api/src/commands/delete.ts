import type { Client } from "@xdevplatform/xdk";

export async function del(
  client: Client,
  args: string[],
): Promise<void> {
  const id = args[0];

  if (!id || id.startsWith("--")) {
    throw new Error("A post ID is required as the first argument.");
  }

  const response = await client.posts.delete(id);
  console.log(JSON.stringify(response, null, 2));
}
