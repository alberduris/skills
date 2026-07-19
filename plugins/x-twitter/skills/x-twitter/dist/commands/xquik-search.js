import { PAGINATION, RAW, TEMPORAL, parseArgs } from "../lib/args.js";
const REQUEST_TIMEOUT_MS = 15_000;
function parseResponse(text) {
    try {
        return JSON.parse(text);
    }
    catch {
        return null;
    }
}
function isSearchResponse(payload) {
    return (payload !== null &&
        typeof payload === "object" &&
        Array.isArray(payload.tweets));
}
export async function xquikSearch(config, args, fetchImpl = fetch) {
    const flags = parseArgs(args, {
        positional: { key: "query", label: "A search query" },
        flags: {
            ...PAGINATION,
            ...TEMPORAL,
            ...RAW,
            "--sort": { key: "sort", type: "string" },
        },
    });
    const limit = flags.maxResults ?? 20;
    if (!Number.isInteger(limit) || limit < 1 || limit > 200) {
        throw new Error("--max-results must be an integer from 1 to 200");
    }
    const sort = flags.sort?.toLowerCase() ?? "latest";
    if (sort !== "latest" && sort !== "top") {
        throw new Error('--sort must be either "latest" or "top"');
    }
    const url = new URL("api/v1/x/tweets/search", `${config.baseUrl.replace(/\/+$/, "")}/`);
    url.searchParams.set("q", flags.query);
    url.searchParams.set("limit", String(limit));
    url.searchParams.set("queryType", sort === "top" ? "Top" : "Latest");
    if (flags.startTime)
        url.searchParams.set("sinceTime", flags.startTime);
    if (flags.endTime)
        url.searchParams.set("untilTime", flags.endTime);
    if (flags.nextToken)
        url.searchParams.set("cursor", flags.nextToken);
    const response = await fetchImpl(url, {
        headers: {
            Accept: "application/json",
            "x-api-key": config.apiKey,
        },
        signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    });
    const payload = parseResponse(await response.text());
    if (!response.ok) {
        throw new Error(`Xquik request failed (${response.status})`);
    }
    if (!isSearchResponse(payload)) {
        throw new Error("Xquik returned an unexpected search response");
    }
    return flags.raw ? payload : payload.tweets;
}
