Lists quote tweets of a specific post. Maps to GET /2/tweets/:id/quote_tweets. Invoke via `node <base_directory>/x.ts quotes <tweet_id> [flags]`. Output is JSON to stdout.

[!FLAGS] a) no flags — returns quote tweets. b) `--max-results <1-100>` — set number of results per page. c) `--next-token <token>` — pagination token from a previous response.

[!OUTPUT-SHAPE] `data` is an array of posts, each embedding the post it quotes.
