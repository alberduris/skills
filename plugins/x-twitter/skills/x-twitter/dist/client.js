import { Client, OAuth1 } from "@xdevplatform/xdk";
/**
 * OAuth 1.0a is always attached; the App-Only bearer is added only when the
 * command needs it.
 *
 * This looks like it could be simplified to "always pass the bearer if we have
 * one" — it cannot. On any GET that accepts several schemes, the SDK's
 * selectAuthMethod prefers the bearer, which drops user context. Fields such as
 * connection_status and receives_your_dm then vanish from responses with no
 * error at all. Attaching it selectively keeps user context by default and
 * still satisfies the handful of endpoints that accept nothing else.
 */
export function createClient(config, mode = "user") {
    const oauth1 = new OAuth1({
        apiKey: config.apiKey,
        apiSecret: config.apiSecret,
        callback: "oob",
        accessToken: config.accessToken,
        accessTokenSecret: config.accessTokenSecret,
    });
    return new Client({
        oauth1,
        ...(mode === "app-only" &&
            config.bearerToken && { bearerToken: config.bearerToken }),
    });
}
