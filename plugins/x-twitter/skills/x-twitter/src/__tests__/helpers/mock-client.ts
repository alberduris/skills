import type { Client } from "@xdevplatform/xdk";

export function mockClient(
  overrides: Record<string, Record<string, unknown>>,
): Client {
  return overrides as unknown as Client;
}
