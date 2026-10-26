import type { ApiResponse } from "../http/client.ts";

/**
 * What every command prints: X's response with `includes` folded into `data`,
 * `meta` and `errors` exactly as X sent them, and our `hints`. Nothing is
 * renamed. `data` is absent only when X sent none, and `errors` then says why.
 */
export interface Output {
  data?: unknown;
  meta?: ApiResponse["meta"];
  errors?: ApiResponse["errors"];
  hints?: string[];
}

/** `data` is X's, or what the command folded `includes` into. */
export function output(
  response: ApiResponse,
  data: unknown = response.data,
  hints: string[] = [],
): Output {
  return {
    data,
    ...(response.meta && { meta: response.meta }),
    ...(response.errors && { errors: response.errors }),
    ...(hints.length > 0 && { hints }),
  };
}
