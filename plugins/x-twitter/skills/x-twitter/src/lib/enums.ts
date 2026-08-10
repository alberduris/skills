const ENUMS: Record<string, { valid: string[]; aliases: Record<string, string> }> = {
  sortOrder: {
    valid: ["recency", "relevancy"],
    aliases: { recent: "recency", relevant: "relevancy", latest: "recency" },
  },
  granularity: {
    valid: ["minute", "hour", "day"],
    aliases: { minutes: "minute", hours: "hour", days: "day", hourly: "hour", daily: "day" },
  },
  replySettings: {
    valid: ["following", "mentionedUsers", "subscribers", "verified"],
    aliases: { friends: "following", mentioned: "mentionedUsers", subs: "subscribers" },
  },
  exclude: {
    valid: ["replies", "retweets"],
    aliases: { rts: "retweets" },
  },
};

/**
 * Narrows a command-line string to the enum a caller expects. The SDK types
 * several of these parameters as literal unions, so callers pass the union as
 * `T`; the cast is safe because every path below either matches `valid`, maps
 * through `aliases` onto a valid value, or throws.
 */
export function resolveEnum<T extends string = string>(
  param: string,
  value: string,
): T {
  const def = ENUMS[param];
  if (!def) return value as T;

  if (def.valid.includes(value)) return value as T;

  const canonical = def.aliases[value];
  if (canonical) return canonical as T;

  const aliasList = Object.entries(def.aliases)
    .map(([k, v]) => `${k}→${v}`)
    .join(", ");
  const hint = aliasList ? ` (aliases: ${aliasList})` : "";
  throw new Error(
    `Invalid value '${value}' for --${param}. Valid: ${def.valid.join(", ")}${hint}`,
  );
}
