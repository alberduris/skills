import type { Config } from "../config.js";

export type AuthMode = "user" | "app-only";

/**
 * Endpoints that accept only the App-Only bearer, or that accept it alongside
 * OAuth 2.0 user context — which these credentials do not have, leaving the
 * bearer as the only usable scheme.
 *
 * Verified against xdk 0.6.6 by running each command with X_API_BEARER_TOKEN
 * unset. Note that `search-news` used to belong here and no longer does: 0.6.6
 * accepts OAuth 1.0a for it. Re-check this list when bumping the SDK.
 */
const APP_ONLY = new Set(["count", "trending", "usage"]);

/** Same, but only on the full-archive variant reached through `--all`. */
const APP_ONLY_WITH_ALL = new Set(["search", "thread"]);

/**
 * Bookmark writes are the one family the X API restricts to OAuth 2.0 user
 * context; OAuth 1.0a and App-Only are both rejected, so no combination of the
 * current credentials can reach them.
 *
 * Reading is not in this set: as of xdk 0.6.6 `GET /2/users/{id}/bookmarks`
 * also accepts OAuth 1.0a, verified live — it returns 402 (authenticated, out
 * of credits) rather than an auth error. It works only because `authModeFor`
 * keeps the bearer off user-context commands.
 */
const NEEDS_OAUTH2_USER = new Set(["bookmark", "unbookmark"]);

export function authModeFor(command: string, args: string[]): AuthMode {
  const needsBearer =
    APP_ONLY.has(command) ||
    (APP_ONLY_WITH_ALL.has(command) && args.includes("--all"));

  return needsBearer ? "app-only" : "user";
}

/**
 * Fails early, with a message naming the missing credential, rather than
 * letting the SDK surface a raw request URL further down.
 */
export function assertCredentials(
  command: string,
  mode: AuthMode,
  config: Config,
): void {
  if (NEEDS_OAUTH2_USER.has(command)) {
    throw new Error(
      `'${command}' requires OAuth 2.0 user context, which this skill does not ` +
        `support. The X API rejects OAuth 1.0a and App-Only for bookmarks, so ` +
        `no combination of X_API_KEY / X_ACCESS_TOKEN / X_API_BEARER_TOKEN can ` +
        `reach them.`,
    );
  }

  if (mode === "app-only" && !config.bearerToken) {
    throw new Error(
      `'${command}' requires X_API_BEARER_TOKEN (OAuth 2.0 App-Only Bearer ` +
        `Token). Generate one in the X Developer Console under ` +
        `Apps > Keys and tokens > Bearer Token.`,
    );
  }
}
