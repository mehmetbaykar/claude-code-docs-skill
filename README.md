# Claude Code Docs Skill

Local Agent Skill mirror of the Anthropic Claude Code documentation from
[https://code.claude.com/docs/en/](https://code.claude.com/docs/en/).

The repository is the skill: `SKILL.md` is the entry point, cleaned Markdown
copies of every relevant Claude Code page live under `references/`, and a
3-hour GitHub Action keeps them in sync with upstream.

## Install

```bash
npx skills add mehmetbaykar/claude-code-docs-skill
```

The `npx skills` CLI handles install, update, and removal across Codex CLI,
Codex IDE/App, Claude Code, Cursor, and other agents that follow the
[agentskills.io](https://agentskills.io) standard.

## Usage

Once installed, invoke the skill with a topic from your agent
(`$claude-code-docs hooks` in Codex, `/claude-code-docs hooks` in Claude Code)
or with no argument to list topics. The full agent-facing usage contract lives
in [SKILL.md](SKILL.md).

## What's mirrored

The fetcher reads the Claude Code sitemap at
`https://code.claude.com/docs/sitemap.xml`, keeps every English documentation
URL whose path starts with `/docs/en/`, and excludes defensive non-core
subtrees:

- `/docs/en/tool-use/*`
- `/docs/en/examples/*`
- `/docs/en/legacy/*`
- `/docs/en/api/*`
- `/docs/en/reference/*`

The mirror contains 132 cleaned Markdown files plus `references/INDEX.md` and
`references/docs_manifest.json`. Any sitemap entries we intentionally skip are
recorded in `docs_manifest.json` under `skipped`.

## Update

```bash
npx skills update claude-code-docs-skill   # update an installed local copy
```

Upstream refreshes happen automatically every 3 hours; there is nothing to
configure on the consumer side.

## Refresh locally (maintainers only)

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
.venv/bin/python scripts/fetch_claude_code_docs.py
```

The fetcher reads the sitemap, downloads each page's `.md` source, cleans MDX
and JSX wrappers into plain Markdown, and rewrites `references/INDEX.md` and
`references/docs_manifest.json`. Files whose content hash is unchanged are not
rewritten.

## Repository layout

```text
.
├── SKILL.md                         # agent-facing instructions and routing
├── agents/anthropic.yaml            # Agent UI metadata + invocation policy
├── references/                      # mirrored Claude Code docs + INDEX + manifest
├── scripts/
│   ├── fetch_claude_code_docs.py    # sitemap -> fetch -> clean -> write
│   └── requirements.txt
└── .github/workflows/
    └── update-docs.yml              # cron every 3 hours
```

## Troubleshooting

- If docs look stale, check the latest run of
[Update Claude Code Documentation](../../actions/workflows/update-docs.yml) on
this repository and reproduce locally with the steps in "Refresh locally" above.
- If the scheduled fetch fails, the workflow opens or updates an issue
automatically.
- If a single page renders poorly, the upstream MDX is preserved under
`references/_raw/` whenever the cleaner falls back, so the source of truth is
never lost.

## Notes

This repository is an unofficial local mirror packaged as an Agent Skill. It is
not affiliated with, endorsed by, or sponsored by Anthropic.

Documentation content belongs to Anthropic and is subject to Anthropic's
applicable terms and policies. The MIT license in this repository applies only
to the mirroring tool, scripts, skill metadata, and repository-specific code.
