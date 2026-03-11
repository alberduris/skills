import type { BeehiivClient } from "../../client.js";

export function mockClient(overrides: Partial<BeehiivClient> = {}): BeehiivClient {
  return {
    get: overrides.get ?? (async () => ({ data: [] })),
    post: overrides.post ?? (async () => ({ data: {} })),
  };
}
