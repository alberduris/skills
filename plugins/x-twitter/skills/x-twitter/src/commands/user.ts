import { path, type Client } from "../http/client.ts";
import { parseArgs } from "../lib/args.ts";
import { USER_FIELDS_EXTENDED } from "../lib/fields.ts";
import { output, type Output } from "./output.ts";

interface UserFlags {
  input: string;
  fields: string[];
}

export async function user(client: Client, args: string[]): Promise<Output> {
  const flags = parseArgs<UserFlags>(args, {
    positional: {
      key: "input",
      label: "A username, user ID, or comma-separated list of IDs",
    },
    flags: {
      "--fields": { key: "fields", type: "string[]" },
    },
    defaults: { fields: USER_FIELDS_EXTENDED },
  });

  const input = flags.input.startsWith("@")
    ? flags.input.slice(1)
    : flags.input;

  const query = { "user.fields": flags.fields };

  // Comma-separated → multiple IDs
  if (input.includes(",")) {
    const ids = input.split(",").map((id) => id.trim());
    const response = await client.get("/2/users", { ids, ...query });
    return output(response, response.data ?? []);
  }

  // All digits → single ID lookup
  if (/^\d+$/.test(input)) {
    const response = await client.get(path`/2/users/${input}`, query);
    return output(response);
  }

  // Otherwise → username lookup
  const response = await client.get(path`/2/users/by/username/${input}`, query);
  return output(response);
}
