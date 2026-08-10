interface ApiErrorShape {
  status: number;
  message: string;
  data: unknown;
}

function isApiError(err: unknown): err is ApiErrorShape {
  return (
    err instanceof Error &&
    "status" in err &&
    "data" in err &&
    typeof (err as { data: unknown }).data === "object"
  );
}

/**
 * Drops query strings from error text while keeping the path. The SDK reports
 * auth failures as plain Errors whose message embeds the whole request URL, so
 * an unredacted message writes the user's search query, IDs and field lists to
 * stderr and into anything that captures it.
 */
function redactQueryStrings(message: string): string {
  return message.replace(/(\/\S*?)\?\S*/g, "$1?<redacted>");
}

/** Renders any thrown value as the lines to write to stderr. */
export function formatError(error: unknown): string[] {
  if (isApiError(error)) {
    const { title, detail, errors } = (error.data ?? {}) as {
      title?: string;
      detail?: string;
      errors?: { message: string }[];
    };

    const headline = [title, detail].filter(Boolean).join(" – ");
    const lines = [`Error: ${headline || redactQueryStrings(error.message)}`];

    for (const e of errors ?? []) {
      lines.push(`  - ${redactQueryStrings(e.message)}`);
    }
    return lines;
  }

  const message = error instanceof Error ? error.message : String(error);
  return [`Error: ${redactQueryStrings(message)}`];
}
