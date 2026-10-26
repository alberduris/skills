import { createHmac, randomBytes } from "node:crypto";

export interface OAuth1Credentials {
  apiKey: string;
  apiSecret: string;
  accessToken: string;
  accessTokenSecret: string;
}

/**
 * RFC 3986 percent-encoding as RFC 5849 §3.6 requires. encodeURIComponent
 * leaves !'()* bare, and any of them in a query would break the signature.
 */
export function percentEncode(value: string): string {
  return encodeURIComponent(value).replace(
    /[!'()*]/g,
    (c) => `%${c.charCodeAt(0).toString(16).toUpperCase()}`,
  );
}

/**
 * Builds the `Authorization: OAuth ...` header for one request (RFC 5849,
 * HMAC-SHA1). `url` is the request URL without its query; `params` are the
 * decoded query parameters. JSON bodies are not signed, per §3.4.1.3.1.
 */
export function oauth1Header(
  method: string,
  url: string,
  params: Record<string, string>,
  credentials: OAuth1Credentials,
  nonce = randomBytes(16).toString("hex"),
  timestamp = String(Math.floor(Date.now() / 1000)),
): string {
  const oauth: Record<string, string> = {
    oauth_consumer_key: credentials.apiKey,
    oauth_nonce: nonce,
    oauth_signature_method: "HMAC-SHA1",
    oauth_timestamp: timestamp,
    oauth_token: credentials.accessToken,
    oauth_version: "1.0",
  };

  const parameterString = Object.entries({ ...params, ...oauth })
    .map(([key, value]) => [percentEncode(key), percentEncode(value)])
    .sort(([a, x], [b, y]) => (a === b ? compare(x, y) : compare(a, b)))
    .map(([key, value]) => `${key}=${value}`)
    .join("&");

  const baseString = [method.toUpperCase(), url, parameterString]
    .map(percentEncode)
    .join("&");
  const signingKey = `${percentEncode(credentials.apiSecret)}&${percentEncode(credentials.accessTokenSecret)}`;
  oauth.oauth_signature = createHmac("sha1", signingKey)
    .update(baseString)
    .digest("base64");

  const fields = Object.entries(oauth)
    .sort(([a], [b]) => compare(a, b))
    .map(([key, value]) => `${percentEncode(key)}="${percentEncode(value)}"`);
  return `OAuth ${fields.join(", ")}`;
}

/** Encoded strings are ASCII, so code-unit order is the byte order the spec sorts by. */
function compare(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0;
}
