Lists available post templates for the publication. Maps to GET /publications/{publicationId}/post_templates. Invoke via `node <base_directory>/beehiiv.js templates [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns up to 10 templates. b) `--limit <1-100>` — results per page. c) `--page <n>` — page number. d) `--raw` — output the full API response envelope.

[!OUTPUT-SHAPE] Default produces an array of template objects with id and name. Use the id with `draft --template-id <id>` to create a draft using a specific template.
