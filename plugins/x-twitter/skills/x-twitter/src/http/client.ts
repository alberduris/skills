import { oauth1Header, percentEncode } from "./oauth1.ts";
import type { OAuth1Credentials } from "./oauth1.ts";

export const BASE_URL = "https://api.x.com";

/**
 * "user" signs with OAuth 1.0a on behalf of the account; "app-only" sends the
 * App-Only bearer, which a few endpoints require and which never carries
 * user-context fields such as connection_status.
 */
export type AuthMode = "user" | "app-only";

/** Query parameters under the names X documents (`tweet.fields`, `max_results`). */
export type Query = Record<string, string | number | readonly string[] | undefined>;

export interface ApiResponse {
  data?: unknown;
  includes?: Record<string, unknown[]>;
  meta?: { next_token?: string; [key: string]: unknown };
  errors?: { message: string; [key: string]: unknown }[];
}

export interface Credentials extends OAuth1Credentials {
  bearerToken?: string;
}

export interface Client {
  get(path: string, query?: Query, auth?: AuthMode): Promise<ApiResponse>;
  post(path: string, body: object): Promise<ApiResponse>;
  put(path: string, body: object): Promise<ApiResponse>;
  delete(path: string): Promise<ApiResponse>;
}

/** A non-2xx response; `data` is the error body X sent back, parsed if JSON. */
export class ApiError extends Error {
  readonly status: number;
  readonly data: unknown;

  constructor(status: number, data: unknown, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

/**
 * Builds a request path, percent-encoding every interpolated value so that an
 * ID such as `1/../../users/me` stays one segment instead of reaching another
 * endpoint.
 */
export function path(strings: TemplateStringsArray, ...values: string[]): string {
  return strings.reduce(
    (out, s, i) => out + s + (i < values.length ? encodeURIComponent(values[i]) : ""),
    "",
  );
}

/**
 * The X API v2 over plain HTTP. Requests are signed with OAuth 1.0a unless
 * the caller passes "app-only". `fetchFn` is the seam tests use to see exactly
 * what goes on the wire.
 */
export function createClient(
  credentials: Credentials,
  fetchFn: typeof fetch = fetch,
): Client {
  function authorization(
    method: string,
    endpoint: string,
    params: Record<string, string>,
    auth: AuthMode,
  ): string {
    if (auth === "user") {
      return oauth1Header(method, BASE_URL + endpoint, params, credentials);
    }
    if (!credentials.bearerToken) {
      throw new Error(
        `${method} ${endpoint} accepts only app-only auth and needs ` +
          `X_API_BEARER_TOKEN (OAuth 2.0 App-Only Bearer Token). Generate one ` +
          `in the X Developer Console under Apps > Keys and tokens > Bearer Token.`,
      );
    }
    return `Bearer ${credentials.bearerToken}`;
  }

  async function send(
    method: string,
    endpoint: string,
    { query = {}, body, auth = "user" }: { query?: Query; body?: object; auth?: AuthMode },
  ): Promise<ApiResponse> {
    const params = queryParams(query);
    const queryString = Object.entries(params)
      .map(([key, value]) => `${percentEncode(key)}=${percentEncode(value)}`)
      .join("&");
    const url = BASE_URL + endpoint + (queryString ? `?${queryString}` : "");

    const headers: Record<string, string> = {
      Authorization: authorization(method, endpoint, params, auth),
    };
    if (body) headers["Content-Type"] = "application/json";

    const response = await fetchFn(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    const text = await response.text();
    if (!response.ok) {
      throw new ApiError(
        response.status,
        parseErrorBody(text),
        `HTTP ${response.status} ${response.statusText} from ${method} ${endpoint}`,
      );
    }
    return JSON.parse(text) as ApiResponse;
  }

  return {
    get: (endpoint, query, auth) => send("GET", endpoint, { query, auth }),
    post: (endpoint, body) => send("POST", endpoint, { body }),
    put: (endpoint, body) => send("PUT", endpoint, { body }),
    delete: (endpoint) => send("DELETE", endpoint, {}),
  };
}

/** Drops unset parameters and joins lists the way X expects them: `a,b,c`. */
function queryParams(query: Query): Record<string, string> {
  const params: Record<string, string> = {};
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined) continue;
    params[key] = Array.isArray(value) ? value.join(",") : String(value);
  }
  return params;
}

function parseErrorBody(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}
