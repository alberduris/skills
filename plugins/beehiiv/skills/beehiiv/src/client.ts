import type { Config } from "./config.js";

export interface BeehiivClient {
  get(path: string, params?: Record<string, string | string[]>): Promise<unknown>;
  post(path: string, body: unknown): Promise<unknown>;
}

const BASE_URL = "https://api.beehiiv.com/v2";

function buildQuery(params: Record<string, string | string[]>): string {
  const parts: string[] = [];
  for (const [key, value] of Object.entries(params)) {
    if (Array.isArray(value)) {
      for (const v of value) {
        parts.push(`${encodeURIComponent(key)}[]=${encodeURIComponent(v)}`);
      }
    } else {
      parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
    }
  }
  return parts.length > 0 ? `?${parts.join("&")}` : "";
}

async function request(
  method: string,
  url: string,
  apiKey: string,
  body?: unknown,
): Promise<unknown> {
  const headers: Record<string, string> = {
    Authorization: `Bearer ${apiKey}`,
    Accept: "application/json",
  };

  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(url, {
    method,
    headers,
    ...(body !== undefined && { body: JSON.stringify(body) }),
  });

  const text = await response.text();

  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const parsed = JSON.parse(text);
      if (parsed.errors) {
        message += `: ${JSON.stringify(parsed.errors)}`;
      } else if (parsed.message) {
        message += `: ${parsed.message}`;
      }
    } catch {
      if (text) message += `: ${text}`;
    }
    throw new Error(message);
  }

  return text ? JSON.parse(text) : undefined;
}

export function createClient(config: Config): BeehiivClient {
  return {
    async get(path, params) {
      const query = params ? buildQuery(params) : "";
      return request("GET", `${BASE_URL}${path}${query}`, config.apiKey);
    },
    async post(path, body) {
      return request("POST", `${BASE_URL}${path}`, config.apiKey, body);
    },
  };
}
