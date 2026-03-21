Lists all publications associated with the API key. Maps to GET /publications. Invoke via `node <base_directory>/beehiiv.js publications [flags]`. Output is JSON to stdout. Does NOT require a publication ID.

[!FLAGS] a) no flags — returns up to 10 publications. b) `--limit <1-100>` — results per page. c) `--page <n>` — page number. d) `--direction <asc|desc>` — sort direction. e) `--order-by <created|name>` — sort field. f) `--expand <comma-list>` — expand fields (e.g. `stats`). g) `--raw` — output the full API response envelope.

[!OUTPUT-SHAPE] Default produces an array of publication objects with id, name, organization_name, referral_program_enabled, created. With `--expand stats`, adds subscription counts and engagement rates. With `--raw`, wraps into the API envelope with `data`, `page`, `limit`, `total_results`, `total_pages`.
