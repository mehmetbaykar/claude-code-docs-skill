# Claude Code Docs Skill

An unofficial mirror of the [Claude Code documentation](https://code.claude.com/docs/en/), packaged as an [Agent Skill](https://agentskills.io) so coding agents read the docs locally instead of searching the web. A GitHub Action refreshes the mirror every 3 hours.

The skill lives in `skills/claude-code-docs/`. The repository is also a plugin, `cc-docs`, for Claude Code, Codex, and Cursor.

## Install

| Agent | Install |
| --- | --- |
| Any agent that reads Agent Skills | `npx skills add mehmetbaykar/claude-code-docs-skill` |
| Claude Code | `/plugin marketplace add mehmetbaykar/claude-code-docs-skill`, then `/plugin install cc-docs@claude-code-docs-skill` |
| Codex | `codex plugin marketplace add mehmetbaykar/claude-code-docs-skill`, then `codex plugin add cc-docs@claude-code-docs-skill` |
| Cursor | In **Customize**, choose **From GitHub Repository** and enter `https://github.com/mehmetbaykar/claude-code-docs-skill`, then install `cc-docs` |

## Use

Ask a Claude Code question and the agent picks up the skill on its own, or call it with a topic:

- Claude Code and Cursor: `/claude-code-docs hooks` (as a Claude Code plugin, also `/cc-docs:claude-code-docs hooks`)
- Codex: `$claude-code-docs hooks`

With no topic, the skill shows what the mirror covers. [`skills/claude-code-docs/SKILL.md`](skills/claude-code-docs/SKILL.md) holds the instructions the agent follows.

## Update

| Installed with | Update |
| --- | --- |
| `npx skills` | `npx skills update claude-code-docs` |
| Claude Code plugin | `claude plugin marketplace update claude-code-docs-skill`, then `claude plugin update cc-docs@claude-code-docs-skill` |
| Codex plugin | `codex plugin marketplace upgrade` |
| Cursor plugin | Import the repository again from **Customize**; team marketplaces can turn on **Enable Auto Refresh** |

Every refresh sets the plugin version to the time of the mirror's last change (`2026.1103.1534` is November 3, 15:34 UTC), so plugin managers see each update.

## What's mirrored

The fetcher reads https://code.claude.com/docs/sitemap.xml and https://code.claude.com/docs/llms.txt and merges both lists, because neither is complete on its own. It mirrors every English page under `/docs/en/` and leaves out other locales, other sites, and these subtrees: `/docs/en/tool-use/`, `/docs/en/examples/`, `/docs/en/legacy/`, `/docs/en/api/`, and `/docs/en/reference/`.

[`references/INDEX.md`](skills/claude-code-docs/references/INDEX.md) lists every page. [`references/docs_manifest.json`](skills/claude-code-docs/references/docs_manifest.json) records each page's upstream URL, content hash, and `live` or `stale` status.

## Freshness guarantees

A refresh builds the whole mirror in memory and publishes it only when every check passes, so a failed run never leaves a half-written mirror. The run fails without publishing when:

- discovery finds no pages, or fewer than 80% of the pages already mirrored
- no page could be fetched live
- more than 20% of pages are stale, have no usable Markdown, or fail cleaning
- a page fails and has no earlier copy to fall back on

A page that fails while an earlier copy exists keeps that copy and is marked `stale`. When cleaning fails, the raw upstream source is kept under `references/_raw/`.

## For maintainers

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python scripts/fetch_docs.py
```

[`scripts/fetch_docs.py`](scripts/fetch_docs.py) holds the Claude Code settings. Everything else in `scripts/`, `tests/`, and `.github/` is shared, byte for byte, with [codex-docs-skill](https://github.com/mehmetbaykar/codex-docs-skill) and [cursor-docs-skill](https://github.com/mehmetbaykar/cursor-docs-skill); `SHARED_FILES` in [`scripts/docs_mirror.py`](scripts/docs_mirror.py) lists the files. Change shared files in all three repositories on branches with the same name: CI's drift check (`python scripts/fetch_docs.py --check-drift`) compares against that branch in the other repositories, or their `main`, and fails while the files differ.

```text
.
├── plugin.json                          # Agent Plugins manifest (Codex, Cursor)
├── .claude-plugin/                      # Claude Code plugin and marketplace (Codex and npx skills read these too)
├── .cursor-plugin/                      # Cursor plugin and marketplace
├── skills/claude-code-docs/
│   ├── SKILL.md                         # instructions the agent follows
│   ├── agents/openai.yaml               # Codex and ChatGPT app metadata
│   └── references/                      # mirrored pages, INDEX.md, docs_manifest.json
├── scripts/
│   ├── fetch_docs.py                    # Claude Code settings
│   └── docs_mirror.py                   # shared engine
├── tests/                               # offline tests
└── .github/workflows/update-docs.yml    # tests, refresh every 3 hours, drift check, failure alerts
```

## Troubleshooting

- **Docs look stale:** check the latest run of [Update docs mirror](../../actions/workflows/update-docs.yml).
- **A scheduled refresh failed:** the workflow opens or updates an issue titled "Docs mirror update failures" and closes it after the next successful run.
- **A page shows `stale`:** upstream could not be reached on the last run, so the previous copy is still served.

## Notes

This is an unofficial mirror, not affiliated with, endorsed by, or sponsored by Anthropic. The documentation belongs to Anthropic and is subject to Anthropic's terms. The MIT license in this repository covers only the mirroring tooling, scripts, and packaging.
