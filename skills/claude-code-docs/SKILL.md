---
name: claude-code-docs
description: >-
  Answers questions about Anthropic's Claude Code from a local mirror of its
  official documentation (code.claude.com/docs). Use when someone asks how
  Claude Code behaves or how to set it up: CLI flags, settings, hooks, skills,
  plugins, MCP servers, subagents, slash commands, permissions, sandboxing,
  memory and CLAUDE.md, output styles, the Agent SDK, the IDE, desktop, web,
  and Slack surfaces, monitoring, or release notes. Read the mirror before
  searching the web. Not for OpenAI Codex, Cursor, the Claude API, or
  claude.ai chat.
license: MIT for the mirroring tooling; the mirrored documentation belongs to Anthropic.
compatibility: Any agent that reads Agent Skills, such as Claude Code, Codex, or Cursor. Needs read access to this skill's files and no network access.
allowed-tools: Read Grep Glob
metadata:
  upstream: https://code.claude.com/docs/en/
  repository: https://github.com/mehmetbaykar/claude-code-docs-skill
---

# Claude Code Docs

A local mirror of the Claude Code documentation, refreshed from code.claude.com every 3 hours. Start at `references/INDEX.md`. Each page is a file `references/<topic>.md` whose frontmatter holds its `title`, `source` URL, and `path`; `references/docs_manifest.json` records every page's upstream URL and status.

## Find the page

1. Turn the topic into a slug: lowercase, drop a leading `/docs/en/`, and join nested segments with `__` (for example `agent sdk hooks` becomes `agent-sdk__hooks`).
2. If `references/<slug>.md` exists, read it.
3. Otherwise read `references/INDEX.md`, pick the closest topics, and read those files. Search the `references/` tree only when the index has no match; the index is faster and keeps context small.
4. With no topic, show the topic groups in `references/INDEX.md`.

## Answer

- Lead with a direct answer grounded in the files you read.
- Quote commands, flags, and settings keys exactly as the page writes them.
- End with `Source: <url>`, using the `source` value from the page's frontmatter.

## When the mirror looks stale or wrong

1. Check the page's `status` in `references/docs_manifest.json`: `stale` means the last refresh could not reach upstream, so the previous copy is still served.
2. Suggest updating the skill with `npx skills update claude-code-docs`, or the `cc-docs` plugin from the agent's plugin manager.
3. Offer the page's `source` URL so the user can check the live page.
4. A page whose cleaning failed keeps its raw upstream source in `references/_raw/<slug>.md`.

## Examples

| Request | Read |
| --- | --- |
| `/claude-code-docs hooks` in Claude Code or Cursor, `$claude-code-docs hooks` in Codex | `references/hooks.md` |
| "How do I add an MCP server?" | `references/mcp.md` |
| "How do hooks work in the Agent SDK?" | `references/agent-sdk__hooks.md` |
| "What can go in settings.json?" | `references/settings.md` |
| "What changed in the latest release?" | `references/changelog.md` |
| No topic, or no matching file | `references/INDEX.md` |
