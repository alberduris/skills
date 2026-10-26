import { readFileSync } from "node:fs";
import { resolve } from "node:path";

export interface Config {
  apiKey: string;
  apiSecret: string;
  accessToken: string;
  accessTokenSecret: string;
  bearerToken?: string;
}

const REQUIRED_VARS = [
  "X_API_KEY",
  "X_API_SECRET",
  "X_ACCESS_TOKEN",
  "X_ACCESS_TOKEN_SECRET",
] as const;

type RequiredVar = (typeof REQUIRED_VARS)[number];

function parseEnvFile(path: string): Record<string, string> {
  try {
    const content = readFileSync(path, "utf-8");
    const vars: Record<string, string> = {};

    for (const line of content.split("\n")) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;

      const eqIndex = trimmed.indexOf("=");
      if (eqIndex === -1) continue;

      const key = trimmed.slice(0, eqIndex).trim();
      const raw = trimmed.slice(eqIndex + 1).trim();
      vars[key] = raw.replace(/^["']|["']$/g, "");
    }

    return vars;
  } catch {
    return {};
  }
}

function resolveVar(
  key: string,
  sources: Record<string, string>[],
): string | undefined {
  for (const source of sources) {
    if (source[key]) return source[key];
  }
  return process.env[key];
}

/**
 * `skillDir` is the directory holding x.ts, wherever the skill is installed;
 * its .env files apply to every project the skill runs from.
 */
export function loadConfig(skillDir: string): Config {
  const cwd = process.cwd();

  // cwd first (project-level), then the skill directory, then the environment
  const sources = [
    parseEnvFile(resolve(cwd, ".env.local")),
    parseEnvFile(resolve(cwd, ".env")),
    parseEnvFile(resolve(skillDir, ".env.local")),
    parseEnvFile(resolve(skillDir, ".env")),
  ];

  const missing: RequiredVar[] = [];
  const get = (key: RequiredVar): string => {
    const value = resolveVar(key, sources);
    if (!value) missing.push(key);
    return value ?? "";
  };

  const config: Config = {
    apiKey: get("X_API_KEY"),
    apiSecret: get("X_API_SECRET"),
    accessToken: get("X_ACCESS_TOKEN"),
    accessTokenSecret: get("X_ACCESS_TOKEN_SECRET"),
  };

  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(", ")}\n` +
        `Set them in .env.local, .env, or as environment variables.`,
    );
  }

  // Optional: only the endpoints that accept nothing but app-only auth need it
  const bearerToken = resolveVar("X_API_BEARER_TOKEN", sources);
  if (bearerToken) {
    config.bearerToken = bearerToken;
  }

  return config;
}
