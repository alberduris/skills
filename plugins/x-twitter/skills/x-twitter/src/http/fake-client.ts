import { createClient, type AuthMode, type Client, type Credentials } from "./client.ts";

/** One request as it left the client: what X would receive. */
export interface SentRequest {
  method: string;
  url: string;
  auth: AuthMode;
  body?: unknown;
}

export const CREDENTIALS: Credentials = {
  apiKey: "test-key",
  apiSecret: "test-secret",
  accessToken: "test-token",
  accessTokenSecret: "test-token-secret",
  bearerToken: "test-bearer",
};

type Route = unknown | ((url: URL) => unknown);

/**
 * A real client over a fake fetch that records every request and answers from
 * `routes`, keyed by "METHOD /path" without the query. A route is a JSON body
 * (sent as 200), a Response, or a function of the URL returning either.
 * Unrouted requests answer `{}`.
 */
export function fakeClient(
  routes: Record<string, Route> = {},
  credentials: Credentials = CREDENTIALS,
): { client: Client; requests: SentRequest[]; headers: Record<string, string>[] } {
  const requests: SentRequest[] = [];
  const headers: Record<string, string>[] = [];

  async function fakeFetch(input: string | URL | Request, init: RequestInit = {}) {
    const url = new URL(String(input));
    const sent = init.headers as Record<string, string>;
    headers.push(sent);
    requests.push({
      method: init.method ?? "GET",
      url: String(input),
      auth: sent.Authorization.startsWith("Bearer ") ? "app-only" : "user",
      ...(init.body ? { body: JSON.parse(init.body as string) } : {}),
    });

    const route = routes[`${init.method} ${url.pathname}`];
    const answer = typeof route === "function" ? route(url) : (route ?? {});
    return answer instanceof Response ? answer : Response.json(answer);
  }

  return { client: createClient(credentials, fakeFetch), requests, headers };
}
