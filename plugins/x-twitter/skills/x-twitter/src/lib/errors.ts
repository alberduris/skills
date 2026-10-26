import { ApiError } from "../http/client.ts";

/** Renders any thrown value as the lines to write to stderr. */
export function formatError(error: unknown): string[] {
  if (error instanceof ApiError && typeof error.data === "object") {
    const { title, detail, errors } = (error.data ?? {}) as {
      title?: string;
      detail?: string;
      errors?: { message: string }[];
    };

    const headline = [title, detail].filter(Boolean).join(" – ");
    const lines = [`Error: ${headline || error.message}`];

    for (const e of errors ?? []) {
      lines.push(`  - ${e.message}`);
    }
    return lines;
  }

  const message = error instanceof Error ? error.message : String(error);
  return [`Error: ${message}`];
}
