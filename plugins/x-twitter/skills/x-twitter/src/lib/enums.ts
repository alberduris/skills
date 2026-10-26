/** Keyed by flag name, so errors name the flag the user typed. */
const ENUMS: Record<string, { valid: string[]; aliases: Record<string, string> }> = {
  sort: {
    valid: ["recency", "relevancy"],
    aliases: { recent: "recency", relevant: "relevancy", latest: "recency" },
  },
  granularity: {
    valid: ["minute", "hour", "day"],
    aliases: { minutes: "minute", hours: "hour", days: "day", hourly: "hour", daily: "day" },
  },
  "reply-settings": {
    valid: ["following", "mentionedUsers", "subscribers", "verified"],
    aliases: { friends: "following", mentioned: "mentionedUsers", subs: "subscribers" },
  },
  exclude: {
    valid: ["replies", "retweets"],
    aliases: { rts: "retweets" },
  },
};

export function resolveEnum(flag: string, value: string): string {
  const def = ENUMS[flag];
  if (!def) return value;

  if (def.valid.includes(value)) return value;

  const canonical = def.aliases[value];
  if (canonical) return canonical;

  const aliasList = Object.entries(def.aliases)
    .map(([k, v]) => `${k}→${v}`)
    .join(", ");
  const hint = aliasList ? ` (aliases: ${aliasList})` : "";
  throw new Error(
    `Invalid value '${value}' for --${flag}. Valid: ${def.valid.join(", ")}${hint}`,
  );
}
