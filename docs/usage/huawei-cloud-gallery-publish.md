# Huawei Cloud Developer Gallery One-Click Publish

Use `huawei-cloud-gallery-publish` when you want an agent to take a trivial web page (typically a CodeArts ACP-generated `index.html`) all the way to a published work in the Huawei Cloud Developer Works Gallery, defaulted to the currently-running 闯关活动 (challenge camp).

The skill is a pure orchestration runbook. It chains three sibling skills that must already exist in the target environment — `huawei-cloud-ext-coding` (CodeArts ACP), `huawei-cloud-jobenv-devbridge-tunnel` (DevBridge tunnel), and `huawei-cloud-publish-work-to-gallery` (publish pipeline) — and encodes the exact ordering, credential handling, and pitfall list that make the flow succeed in a single pass.

If you are still choosing among skills, use the [Skill Matrix](skill-matrix.md). For installation only, use the [Quickstart](quickstart.md).

## Best Fit

Use this skill when you need to:

- Generate a simple Hello World-style webpage with CodeArts ACP and expose it over a public tunnel URL
- Push the source to a fresh GitCode repository (OAuth flow included) without leaking STS credentials into git
- Produce the full set of gallery assets: cover image, 29-char intro, architecture diagram, detail zip
- Publish to the Huawei Cloud Developer Works Gallery, picking an active training camp (default 闯关活动) with one user confirmation
- Avoid the known pitfalls: bwrap mount-namespace file access, OAuth link timing, STS 900s expiry, GitCode `private_token` auth, single-commit discipline

Avoid when you need to publish a large multi-service project, need CI/CD-driven repeated publishing, or the environment lacks the three sibling skills / `hcloud` CLI.

## How It Works

```text
Phase 1: Page Gen (ACP)   Phase 2: Host workDir     Phase 3: Publish pipeline (huawei-cloud-publish-work-to-gallery)
┌───────────────────┐   ┌──────────────────────┐   ┌──────────────────────────────────────────────────────┐
│ healthz ACP 19300 │   │ mkdir workspace dir  │   │ S1 STS creds  → S2 devbridge tunnel → S3 GitCode  │
│ acpx session gen  │──►│ cp /proc/<pid>/cwd/  │──►│ repo+push     → S4 cover.png        → S5 intro  │
│ index.html + :8000│   │ + README.md          │   │ S6 detail.zip → S7 pick camp (user) → S8 publish│
└───────────────────┘   └──────────────────────┘   └──────────────────────────────────────────────────────┘
```

Only two user interactions: one GitCode OAuth browser authorization, one camp selection at Step 7. Everything else is autonomous.

## What's Bundled

- `SKILL.md` — the complete 3-phase / 8-step operating procedure plus the 9-item pitfall checklist. The skill intentionally ships no scripts: all executable tooling lives in the three sibling skills it orchestrates.

## Quick Workflow

1. **Prereq check**: confirm `huawei-cloud-ext-coding`, `huawei-cloud-jobenv-devbridge-tunnel`, `huawei-cloud-publish-work-to-gallery` are installed in the target env and `hcloud` is logged in.
2. **Trigger**: say “帮我把这个简单网页发布到华为云开发者作品展览馆” — the agent generates the page, hosts it on port 8000, and runs the 8-step publish pipeline.
3. **Authorize**: when the GitCode OAuth link appears, open it in a browser immediately (the agent waits up to 300s, and regenerates the link on timeout).
4. **Confirm camp**: pick the training camp by index when prompted (default recommendation: 闯关活动).
5. **Done**: the agent returns the gallery work URL; the tunnel is intentionally left running for verification.

## Share & Install

Recommend this skill to a teammate with either link:

- Raw `SKILL.md` (paste-into-AI friendly): `https://raw.githubusercontent.com/dengyie/awesome-skills/main/huawei-cloud-gallery-publish/SKILL.md`
- Package page on GitHub: `https://github.com/dengyie/awesome-skills/tree/main/huawei-cloud-gallery-publish`

One-command install for Codex / ZCode / Claude Code / Cursor / Windsurf / Gemini CLI:

```bash
mkdir -p ~/.agents/skills/huawei-cloud-gallery-publish
curl -fsSL https://raw.githubusercontent.com/dengyie/awesome-skills/main/huawei-cloud-gallery-publish/SKILL.md \
  -o ~/.agents/skills/huawei-cloud-gallery-publish/SKILL.md
```

Restart the agent (or reload skills) and trigger with `$huawei-cloud-gallery-publish`.

**Heads-up for the recipient**: this skill is a pure orchestration runbook. It presumes the sibling skills `huawei-cloud-ext-coding`, `huawei-cloud-jobenv-devbridge-tunnel`, and `huawei-cloud-publish-work-to-gallery`, plus a logged-in `/usr/local/bin/hcloud` and `/root/job-envs/registry.json`, already exist in the target environment. Installing this skill alone in a fresh environment will not run the pipeline end-to-end.

For the full repository-level install path, see the [Quickstart](quickstart.md).

## Pitfalls The Skill Guards Against

- Sandbox page files are invisible from the host — must be read via `/proc/<http-server-pid>/cwd/`
- `git init` must be preceded by a `.gitignore` excluding `sts-creds.json` / `sts-creds.sh`
- Only one commit, before any binary assets exist; Step 4+ artifacts go to `/tmp`, never the workDir
- GitCode API uses `private_token` query param and the `access_token` field of `auth.toml`
- STS must be refreshed right before publish (900s TTL vs. multi-minute pipeline)
- The gallery intro uses a pre-validated 29-CJK-char sentence — do not draft long then trim
