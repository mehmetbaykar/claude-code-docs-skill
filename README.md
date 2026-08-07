# Claude Code Docs Skill

Local Agent Skill mirror of the Anthropic Claude Code documentation from
[https://code.claude.com/docs/en/](https://code.claude.com/docs/en/).

The installable skill lives in `skills/claude-code-docs/`: `SKILL.md` is the
entry point, cleaned Markdown copies of every relevant Claude Code page live
under `skills/claude-code-docs/references/`, and a 3-hour GitHub Action keeps
them in sync with upstream.

## Install

```bash
npx skills add mehmetbaykar/claude-code-docs-skill
```

The `npx skills` CLI discovers the nested skill automatically. Installing the
repo exposes only the skill directory (`SKILL.md`, provider metadata in
`agents/`, and `references/`) to the target agent while repository maintenance
files stay at the repo root.

## Usage

Once installed, invoke the skill with a topic from your agent
(`$claude-code-docs hooks` in Codex, `/claude-code-docs hooks` in Claude Code)
or with no argument to list topics. The full agent-facing usage contract lives
in [skills/claude-code-docs/SKILL.md](skills/claude-code-docs/SKILL.md).

## What's mirrored

The fetcher discovers pages from the Claude Code sitemap at
`https://code.claude.com/docs/sitemap.xml` and the machine-readable index at
`https://code.claude.com/docs/llms.txt`, then merges both sets. It keeps every
English documentation URL whose path starts with `/docs/en/`, and excludes
defensive non-core subtrees:

- `/docs/en/tool-use/*`
- `/docs/en/examples/*`
- `/docs/en/legacy/*`
- `/docs/en/api/*`
- `/docs/en/reference/*`

Non-English locale trees and cross-domain URLs are excluded as well. The mirror
tracks the full English documentation set; the current page count, per-page
status, and any intentionally skipped entries are recorded in
`skills/claude-code-docs/references/docs_manifest.json`, and the generated topic
list lives in `skills/claude-code-docs/references/INDEX.md`.

## Update

```bash
npx skills update claude-code-docs-skill   # update an installed local copy
```

Upstream refreshes happen automatically every 3 hours; there is nothing to
configure on the consumer side.

## Refresh locally (maintainers only)

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements-dev.txt
.venv/bin/python -m pytest tests -q
.venv/bin/python scripts/fetch_claude_code_docs.py
```

The fetcher discovers pages, downloads each page's `.md` source, cleans MDX
and JSX wrappers into plain Markdown, and rewrites
`skills/claude-code-docs/references/INDEX.md` and
`skills/claude-code-docs/references/docs_manifest.json`. Files whose content
hash is unchanged are not rewritten.

## Freshness guarantees

The mirror fails loudly rather than serving frozen content. A run aborts
without committing when:

- discovery returns no pages
- no page could be fetched live
- discovery drops below 80% of the previously mirrored page count
- more than 20% of pages served stale content or exposed no usable Markdown
- any page failed outright

Every entry in `docs_manifest.json` records a `status` of `live` or `stale`,
and `fetch_metadata` reports live, stale, skipped, and failed counts for the
run.

## Repository layout

```text
.
├── skills/
│   └── claude-code-docs/
│       ├── agents/
│       │   └── openai.yaml               # Agent UI metadata + invocation policy
│       ├── SKILL.md                      # installed skill instructions and routing
│       └── references/                   # mirrored docs + INDEX + manifest
├── scripts/
│   ├── fetch_claude_code_docs.py         # discover -> fetch -> clean -> write
│   ├── requirements.txt
│   └── requirements-dev.txt
├── tests/
│   └── test_fetch_claude_code_docs.py    # offline tests for the fetcher
└── .github/workflows/
    └── update-docs.yml                   # tests on PRs, cron refresh every 3 hours
```

## Troubleshooting

- If docs look stale, check the latest run of
[Update Claude Code Documentation](../../actions/workflows/update-docs.yml) on
this repository and reproduce locally with the steps in "Refresh locally" above.
- If the scheduled fetch fails, the workflow opens or updates a failure issue
  automatically and closes it after the next successful run.
- If a page reports `stale` in `docs_manifest.json`, the previous content is
  still served but upstream could not be reached on the last run.
- If a single page renders poorly, the upstream MDX is preserved under
  `skills/claude-code-docs/references/_raw/` whenever the cleaner falls back, so
  the source of truth is never lost.

## Notes

This repository is an unofficial local mirror packaged as an Agent Skill. It is
not affiliated with, endorsed by, or sponsored by Anthropic.

Documentation content belongs to Anthropic and is subject to Anthropic's
applicable terms and policies. The MIT license in this repository applies only
to the mirroring tool, scripts, skill metadata, and repository-specific code.
