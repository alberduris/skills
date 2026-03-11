Retrieves a single publication's details. Maps to GET /publications/{publicationId}. Invoke via `node <base_directory>/beehiiv.js publication [flags]`. Output is JSON to stdout. Uses the configured publication ID by default; override with `--pub-id <id>`.

[!FLAGS] a) no flags — returns the publication with stats expanded by default. b) `--expand <comma-list>` — override expand fields. c) `--raw` — output the full API response envelope.

[!OUTPUT-SHAPE] Default produces the publication object directly with id, name, organization_name, referral_program_enabled, created, and stats (active_subscriptions, average_open_rate, average_click_rate, etc.).
