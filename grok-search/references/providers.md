# Providers, Limits, And Run Records

Read this when a result mentions a skipped or failed provider, when configuration errors appear, or when you need the durable record of a run.

## Provider Order

- `search.js`: Grok Responses runs alongside independent Tavily Search (needs `TAVILY_API_KEY`), Firecrawl Search (keyless by default, `FIRECRAWL_API_KEY` when set), and Exa Search (needs `EXA_API_KEY`). Extras are never fed into Grok. `--extra N` (default 6) is the per-channel target: every configured channel searches N results on its own, then `mergeSources` dedupes the union by normalized URL (tracking params stripped, cleanest URL kept, `merged_from` listing every channel whose duplicate merged in); `--no-extra` disables all extras and the degraded fallback. On `--source x` extras are off unless `--extra N` is given (`extra_mode: "off-x-only"`).
- `fetch.js --provider auto`: Tavily Extract → Firecrawl Scrape → Exa Contents (needs `EXA_API_KEY`, about $0.001 per page, `cost_usd` on the attempt) → Direct Fetch. Without a key Exa is just a skipped attempt. Exception: X post URLs try Direct first regardless of keys (`references/x-search.md`).
- `map.js --provider auto`: Tavily Map → Direct Map.
- `--responses-openrouter-engine exa` forces a web-only engine on OpenRouter.

Domain filters apply to all channels: `--responses-allowed-domains` / `--responses-excluded-domains` are pushed to Tavily (`include_domains`/`exclude_domains`), Firecrawl and Exa (`includeDomains`/`excludeDomains`). Anything that still comes back off-domain is ranked after Grok's own results, not dropped. `diagnostics.options.extra_domain_filter` reports `pushed`, `demoted`, or `none`; extra attempts report `off_domain`.

Direct is this repo's own fallback: a plain HTTP GET through Node's `fetch` (undici, honoring the proxy settings) with a `grok-search-skill/0.1` user agent, following redirects, capped at 2 MB, rejecting binary and attachment responses, then stripping HTML to text with regexes (scripts, styles, nav noise are only partly removed). It does not execute JavaScript, log in, use cookies, parse PDFs, or bypass anti-bot; its text is noisier than Tavily's or Firecrawl's and can lose body content on some layouts. Direct Map only reads `/sitemap.xml` and same-domain homepage links, ignores `--instructions`, and is limited to `--max-depth 1`. Neither Direct nor the paid providers get anything useful from Reddit or YouTube pages.

## Firecrawl And Exa Quota Cooldowns

Firecrawl keyless has a rolling daily quota per IP. When it is exhausted the API answers 429 with `reason: credits` and a `retry_after_seconds` that is usually hours. The scripts then:

- stop retrying immediately (a `Retry-After` beyond the retry budget means "not now", not "wait a bit");
- write `<stateDir>/firecrawl-cooldown.json` (`until`, `auth_mode`, `reason`, `hit_at`), default `~/.cache/grok-search/`;
- skip Firecrawl in every later `auto` command until `until` passes. Skips appear in `diagnostics.provider_attempts` as `{ provider: "firecrawl", skipped: true, error: "cooldown until <ISO> (credits)" }`. For search, the slots go to Tavily when configured, otherwise extras are empty and a warning says so.

An explicit `--provider firecrawl` ignores the cooldown and clears it on success. The cooldown is scoped to `auth_mode`, so adding an API key takes effect immediately. Set `GROK_STATE_DIR` to move the state file.

Exa answers an empty balance with HTTP 402 and gets the same treatment: the scripts stop retrying, write `<stateDir>/exa-cooldown.json`, and skip Exa in later `auto` runs (search slots go to the remaining channels). An explicit `--provider exa` still makes the request and clears the cooldown on success.

Retry policy in general: HTTP 408/429/500/502/503/504 retry up to 3 times with backoff, honoring `Retry-After` (header or Firecrawl's `retry_after_seconds`) when it fits the budget. Bad JSON, `success:false` bodies, 4xx such as 403 "IP looks suspicious", and scrape timeouts are not retried. Attempts report `requests` (HTTP calls made) and `duration_ms`.

## Relay Behaviour

The Responses endpoint is usually reached through an OpenAI-compatible relay, and relays differ in ways that change cost and output: one served `grok-4.5-build` for every `grok-4.5` request (two to three times the tool calls and cost), one drops `parallel_tool_calls` (the parameter works against `api.x.ai` directly; `max_tool_calls` does not, anywhere), grok-4.5 through one relay returned its between-call narration as extra `message` items (grok-4.6 through the same relay does not), one returns X search as `custom_tool_call` items. `usage.cost_in_usd_ticks`, and so `diagnostics.cost_usd`, is whatever the endpoint reports: one relay reported 40% of xAI's own figure for identical token and call counts, so compare cost across providers by tokens and calls, not by this field. `diagnostics.responses_model` is the model the relay actually served; a warning is added when it differs from the requested one. Narration messages are dropped from `answer.text` (the last message is the answer; earlier ones stay only when long or cited).

## Grok Failures

Grok failures split into named failures and degrade-able failures. Quota (402/403 with a quota error code such as `insufficient_user_usd_credit`, or a body mentioning quota/credits/billing/balance) is named even without extras: `grok_error.code: QUOTA_EXHAUSTED`; a surviving 429 is `RATE_LIMITED`. When extras are available, four more cases degrade instead of erroring: `NO_SEARCH` (the relay dropped web_search and answered from memory), `EMPTY` (empty content), `TIMEOUT` (timeout / 408 / 504 / 524), and `UPSTREAM` (5xx) — in all cases `diagnostics.degraded: true` and a visibly marked raw Tavily/Firecrawl/Exa answer. The per-request timeout scales with the command deadline (`grokRequestTimeoutMs`: min 180s, deadline minus a 20s reserve, floor 8s) so a hung POST cannot eat the whole budget. Plain auth and protocol errors (401/403/422 without a quota body) stay hard failures even when extras exist. Other Grok failures are errors. If `search.js` returns `GROK_API_URL 未配置` or `GROK_API_KEY 未配置`, the project is missing required setup; point the user at `README.md` rather than working around it.

## Source Cards

- `source_type`: `citation` (used in the answer), `searched` (listed by a search call), `extra` (Tavily/Firecrawl/Exa). `opened: true` marks pages Grok actually read (from `open_page` actions; web only, X search has no trace). Rank: citation > opened > in-domain extra > searched > off-domain extra.
- Duplicate URLs across channels are merged into one card; `merged_from` lists the providers that contributed fields. A placeholder title such as `"1"` or `[2]` counts as missing: a real title replaces it, otherwise the card has no `title`.
- `diagnostics.responses_tool_calls` is `{ total, upstream: { web, x } | null, trace: { web, x }, by_action: { search, open_page, find_in_page }, failed? }`. `total` is the per-tool maximum of the billing usage and the trace; the two raw tallies stay visible because relays under-report either side. `grok_tool_calls[].source_count` in the run record is a relay-cumulative value, not per call.
- Fetch `metadata`: `{ title, description, author, published_at, language, status, source_url }` from Firecrawl; Exa adds `title / author / published_at / source_url`; Direct adds `status`, `content_type`, `content_length`, `content_disposition`.

## Run Records

Every command writes one JSON run record to the output directory (`~/.cache/grok-search/outputs/`, `GROK_OUTPUT_DIR` overrides). Search exposes it as `sources.raw_path` (always set), fetch and map as `diagnostics.run_path`. Records are also written on errors and on `DEADLINE_EXCEEDED`.

Search records hold `argv` (secrets redacted), `query`, `instructions`, `options`, the full `answer`, `sources.grok` / `sources.extra` / `sources.items` (uncapped), `provider_attempts`, `grok_tool_calls`, and `diagnostics`. Fetch records hold the full content and `metadata`; map records hold `urls`. `GROK_DEBUG_RAW=1` or `--full-sources` also embeds the redacted Grok response as `grok_raw`. `GROK_RUN_LOG=off` (or `runLog: false`) disables records; `raw_path` / `run_path` become null. Files older than 30 days are cleaned up on each run.

## Proxy

The scripts use terminal proxy variables via undici: `HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY` and lowercase variants; `NO_PROXY` is honored and loopback hosts bypass. `GROK_PROXY="http://127.0.0.1:7890"` sets a proxy for this tool only, `GROK_PROXY=off` forces direct connections, `GROK_DEBUG=true` prints proxy and retry debug lines to stderr.
