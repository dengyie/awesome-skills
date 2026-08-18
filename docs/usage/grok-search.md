# Grok Search

Use `grok-search` when a task needs live web access: current facts, a specific URL read, or discovery of what pages exist on a site.

The package is a set of Node scripts rather than an MCP server or extension. Each script writes one JSON object to stdout, so results are machine-readable and cheap to skim before deciding what to read in depth.

If you are still choosing among skills, use the [Skill Matrix](skill-matrix.md). For installation only, use the [Quickstart](quickstart.md).

## Best Fit

Use this skill when you need to:

- check latest or current information that stable model knowledge cannot answer
- read what a specific URL actually says
- discover candidate pages on a site before reading any of them
- compare several independent sources on the same question

Do not use it for local code search or for stable offline knowledge unless the user explicitly asks for live web access.

## Requirements

- Node.js `>=18.17`
- one `npm install` in the skill directory to install the `undici` transport dependency
- `GROK_API_URL` and `GROK_API_KEY` configured for `scripts/search.js`

Long-lived keys belong in `~/.config/grok-search/config.json`, created from `config.example.json`:

```bash
mkdir -p ~/.config/grok-search
cp config.example.json ~/.config/grok-search/config.json
chmod 600 ~/.config/grok-search/config.json
```

Keep credentials out of the repository. `config.example.json` is a template with empty and placeholder values only.

## Choose The Script

Route by what the request already gives you:

- a URL, and the question is what it says: `scripts/fetch.js`
- a named site but no URL, and the question is what is on it: `scripts/map.js`, then fetch the URLs you pick
- current information, or the URL is unknown: `scripts/search.js`

Run the fewest commands that answer the question. Do not chain map, fetch, and search by default. When sub-questions are independent, run the commands in parallel.

```bash
./scripts/search.js "latest Node.js LTS"
./scripts/fetch.js https://example.com
./scripts/map.js https://docs.example.com --limit 20
```

## Reading Results

Check `error` first. If it is present, read `error.message`, `error.code`, and `diagnostics.provider_attempts`, then change something before retrying: a sharper query, a different `--provider` for fetch and map, or a different `--model` for search. Rerunning the same command is not a retry strategy.

On success, read `answer.text` and `sources.merged` for search, `content.text` for fetch, and `urls` for map. Also inspect `diagnostics.warnings`, `diagnostics.degraded`, and `sources.grok[].source_type` before treating sources as evidence: a degraded answer is built from raw Tavily and Firecrawl results when Grok quota is exhausted, and it is marked as such.

Search source payloads are referenced by `sources.raw_path`. Fetch writes complete truncated content to disk but omits the machine-local path by default; rerun with `--full-path` only when the path is needed, then read the file in chunks.

```bash
./scripts/fetch.js --full-path https://example.com
```

## Providers And Limits

For `--provider auto`, `fetch.js` tries Tavily Extract, then Firecrawl Scrape, then Direct Fetch; `map.js` tries Tavily Map, then Direct Map. Tavily requires a key, Firecrawl works on its keyless tier, and the direct providers do not execute JavaScript, log in, use cookies, parse PDFs, or bypass anti-bot measures.

Proxy environment variables are picked up automatically, including `HTTP_PROXY`, `HTTPS_PROXY`, and `ALL_PROXY` with lowercase variants. `NO_PROXY` is honored and loopback hosts are bypassed. Use `GROK_PROXY` to set a proxy for this tool alone, or `GROK_PROXY=off` to force direct connections.

## Verification

From the skill directory:

```bash
npm install
npm test
```

Package structure and documentation wiring are checked from the repository root:

```bash
python3 -m unittest discover grok-search/tests -v
```

## Prompt

```text
Use $grok-search to check the current state of this topic on the live web and cite the sources you actually read.
```

## Related Docs

- [Skill Matrix](skill-matrix.md)
- [Quickstart](quickstart.md)
- [Troubleshooting](troubleshooting.md)
- [Golden Path](golden-path.md)
