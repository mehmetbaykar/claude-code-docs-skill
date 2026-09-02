---
title: "Explore the .claude directory"
source: https://code.claude.com/docs/en/claude-directory
path: /docs/en/claude-directory
---

# Explore the .claude directory

> Where Claude Code reads CLAUDE.md, settings.json, hooks, skills, commands, subagents, workflows, rules, and auto memory. Explore the .claude directory in your project and ~/.claude in your home directory.

Claude Code reads instructions, settings, skills, subagents, and memory from your project directory and from `~/.claude` in your home directory. Commit project files to git to share them with your team; files in `~/.claude` are personal configuration that applies across all your projects.

On Windows, `~/.claude` resolves to `%USERPROFILE%\.claude`. If you set [`CLAUDE_CONFIG_DIR`](https://code.claude.com/docs/en/env-vars), every `~/.claude` path on this page lives under that directory instead.

Most users only edit `CLAUDE.md` and `settings.json`. The rest of the directory is optional: add skills, rules, or subagents as you need them.

## Explore the directory

Click files in the tree to see what each one does, when it loads, and an example.

## What's not shown

The explorer covers files you author and edit. A few related files live elsewhere:

| File                    | Location                   | Purpose                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ----------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `managed-settings.json` | System-level, varies by OS | Enterprise-enforced settings that you can't override, apart from [narrow exceptions](https://code.claude.com/docs/en/settings#security-keys-where-the-stricter-value-applies). See [where to save the file](https://code.claude.com/docs/en/managed-settings#deploy-a-managed-settings-file) and [which managed source Claude Code uses](https://code.claude.com/docs/en/managed-settings#precedence-within-the-managed-tier).                                                                                                                               |
| `CLAUDE.local.md`       | Project root               | Your private preferences for this project, loaded alongside CLAUDE.md. Create it manually and add it to `.gitignore`.                                                                                                                                                                                                                                                                                                                                                    |
| Installed plugins       | `~/.claude/plugins`        | Cloned marketplaces, installed plugin versions, and per-plugin data, managed by `claude plugin` commands. For a plugin installed from a marketplace [`command` source](https://code.claude.com/docs/en/plugin-marketplaces#command-sources) in link mode, Claude Code stores links here instead of a copy, and the plugin's files stay in the directory the command prints. See [plugin caching](https://code.claude.com/docs/en/plugins-reference#plugin-caching-and-file-resolution) for how orphaned versions are cleaned up. |

`~/.claude` also holds data Claude Code writes as you work: transcripts, prompt history, file snapshots, caches, and logs. See [application data](#application-data) below.

## Choose the right file

Different kinds of customization live in different files. Use this table to find where a change belongs.

| You want to                                        | Edit                                     | Scope             | Reference                                           |
| :------------------------------------------------- | :--------------------------------------- | :---------------- | :-------------------------------------------------- |
| Give Claude project context and conventions        | `CLAUDE.md`                              | project or global | [Memory](https://code.claude.com/docs/en/memory)                                |
| Allow or block specific tool calls                 | `settings.json` `permissions` or `hooks` | project or global | [Permissions](https://code.claude.com/docs/en/permissions), [Hooks](https://code.claude.com/docs/en/hooks)  |
| Run a script before or after tool calls            | `settings.json` `hooks`                  | project or global | [Hooks](https://code.claude.com/docs/en/hooks)                                  |
| Set environment variables for the session          | `settings.json` `env`                    | project or global | [Settings](https://code.claude.com/docs/en/settings-reference#all-settings)     |
| Keep personal overrides out of git                 | `settings.local.json`                    | project only      | [Settings scopes](https://code.claude.com/docs/en/settings#where-settings-live) |
| Add a prompt or capability you invoke with `/name` | `skills/<name>/SKILL.md`                 | project or global | [Skills](https://code.claude.com/docs/en/skills)                                |
| Define a specialized subagent with its own tools   | `agents/*.md`                            | project or global | [Subagents](https://code.claude.com/docs/en/sub-agents)                         |
| Orchestrate many subagents from a script           | `workflows/*.js`                         | project or global | [Dynamic workflows](https://code.claude.com/docs/en/workflows)                  |
| Connect external tools over MCP                    | `.mcp.json`                              | project only      | [MCP](https://code.claude.com/docs/en/mcp)                                      |
| Change how Claude formats responses                | `output-styles/*.md`                     | project or global | [Output styles](https://code.claude.com/docs/en/output-styles)                  |

## File reference

This table lists every file the explorer covers. Project-scope files live in your repo under `.claude/` (or at the root for `CLAUDE.md`, `.mcp.json`, and `.worktreeinclude`). Global-scope files live in `~/.claude/` and apply across all projects.

Several things can override what you put in these files:

* [Managed settings](https://code.claude.com/docs/en/server-managed-settings) deployed by your organization take precedence over everything, apart from the [exceptions under Settings precedence](https://code.claude.com/docs/en/settings#exceptions-to-managed-settings-precedence)
* CLI flags like `--permission-mode` or `--settings` override `settings.json` for that session
* Some environment variables take precedence over their equivalent setting, but this varies: check the [environment variables reference](https://code.claude.com/docs/en/env-vars) for each one

See [settings precedence](https://code.claude.com/docs/en/settings#settings-precedence) for the full order.

Click a filename to open that node in the explorer above.

| File                                                | Scope              | Commit | What it does                                                                                                  | Reference                                                       |
| --------------------------------------------------- | ------------------ | ------ | ------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| [`CLAUDE.md`](#ce-claude-md)                        | Project and global | ✓      | Instructions loaded every session                                                                             | [Memory](https://code.claude.com/docs/en/memory)                                            |
| [`rules/*.md`](#ce-rules)                           | Project and global | ✓      | Topic-scoped instructions, optionally path-gated                                                              | [Rules](https://code.claude.com/docs/en/memory#organize-rules-with-claude/rules/)           |
| [`settings.json`](#ce-settings-json)                | Project and global | ✓      | Permissions, hooks, env vars, model defaults                                                                  | [Settings](https://code.claude.com/docs/en/settings)                                        |
| [`settings.local.json`](#ce-settings-local-json)    | Project only       |        | Your personal overrides, gitignored when Claude Code saves a setting to it                                    | [Settings scopes](https://code.claude.com/docs/en/settings#where-settings-live)             |
| [`.mcp.json`](#ce-mcp-json)                         | Project only       | ✓      | Team-shared MCP servers                                                                                       | [MCP scopes](https://code.claude.com/docs/en/mcp#mcp-installation-scopes)                   |
| [`.worktreeinclude`](#ce-worktreeinclude)           | Project only       | ✓      | Gitignored files to copy into new worktrees                                                                   | [Worktrees](https://code.claude.com/docs/en/worktrees#copy-gitignored-files-into-worktrees) |
| [`skills/<name>/SKILL.md`](#ce-skills)              | Project and global | ✓      | Reusable prompts invoked with `/name` or auto-invoked                                                         | [Skills](https://code.claude.com/docs/en/skills)                                            |
| [`commands/*.md`](#ce-commands)                     | Project and global | ✓      | Single-file prompts; same mechanism as skills                                                                 | [Skills](https://code.claude.com/docs/en/skills)                                            |
| [`output-styles/*.md`](#ce-output-styles)           | Project and global | ✓      | Custom system-prompt sections                                                                                 | [Output styles](https://code.claude.com/docs/en/output-styles)                              |
| [`agents/*.md`](#ce-agents)                         | Project and global | ✓      | Subagent definitions with their own prompt and tools                                                          | [Subagents](https://code.claude.com/docs/en/sub-agents)                                     |
| [`workflows/*.js`](#ce-workflows)                   | Project and global | ✓      | Dynamic workflow scripts written by Claude and saved from `/workflows`; each file becomes a `/<name>` command | [Dynamic workflows](https://code.claude.com/docs/en/workflows)                              |
| [`agent-memory/<name>/`](#ce-agent-memory)          | Project and global | ✓      | Persistent memory for subagents                                                                               | [Persistent memory](https://code.claude.com/docs/en/sub-agents#enable-persistent-memory)    |
| [`~/.claude.json`](#ce-claude-json)                 | Global only        |        | App state, OAuth, UI toggles, personal MCP servers                                                            | [Global config](https://code.claude.com/docs/en/settings-reference#global-config-settings)  |
| [`projects/<project>/memory/`](#ce-global-projects) | Global only        |        | Auto memory: Claude's notes to itself across sessions                                                         | [Auto memory](https://code.claude.com/docs/en/memory#auto-memory)                           |
| [`keybindings.json`](#ce-keybindings)               | Global only        |        | Custom keyboard shortcuts                                                                                     | [Keybindings](https://code.claude.com/docs/en/keybindings)                                  |
| [`themes/*.json`](#ce-themes)                       | Global only        |        | Custom color themes                                                                                           | [Custom themes](https://code.claude.com/docs/en/terminal-config#create-a-custom-theme)      |

## Troubleshoot configuration

If a setting, hook, or file isn't taking effect, see [Debug your configuration](https://code.claude.com/docs/en/debug-your-config) for the inspection commands and a symptom-first lookup table.

## Application data

Beyond the config you author, `~/.claude` holds data Claude Code writes during sessions. These files are plaintext. Anything that passes through a tool lands in a transcript on disk: file contents, command output, pasted text.

### Cleaned up automatically

Claude Code deletes the files in the paths below once they're older than [`cleanupPeriodDays`](https://code.claude.com/docs/en/settings-reference#cleanupperioddays), as long as it can safely determine the retention period. The default is 30 days and the minimum is 1; setting `0` fails with a validation error. The same age cutoff applies to automatic removal of [orphaned worktrees](https://code.claude.com/docs/en/worktrees#clean-up-subagent-and-background-session-worktrees).

| Path under `~/.claude/`                                                                                                         | Contents                                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `projects/<project>/<session>.jsonl`                                                                                            | Full conversation transcript: every message, tool call, and tool result                                                                                                                                                                                                                              |
| `projects/<project>/<session>.orphaned-<timestamp>-<suffix>.jsonl`, `projects/<project>/<session>.jsonl.superseded-<timestamp>` | A previous transcript for the session that Claude Code set aside instead of overwriting or deleting it. It doesn't appear in the session picker                                                                                                                                                      |
| `projects/<project>/<session>/subagents/`                                                                                       | [Subagent](https://code.claude.com/docs/en/sub-agents) conversation transcripts, removed with the parent session transcript when it ages out                                                                                                                                                                                     |
| `projects/<project>/<session>/tool-results/`                                                                                    | Large tool outputs spilled to separate files                                                                                                                                                                                                                                                         |
| `file-history/<session>/`                                                                                                       | Pre-edit snapshots of files Claude changed, used for [checkpoint restore](https://code.claude.com/docs/en/checkpointing). Holds snapshots for the 100 most recent checkpoints; snapshot files that no retained checkpoint references are deleted, except each file's first snapshot                                              |
| `plans/`                                                                                                                        | Plan files written during [plan mode](https://code.claude.com/docs/en/permission-modes#analyze-before-you-edit-with-plan-mode)                                                                                                                                                                                                   |
| `debug/`                                                                                                                        | Per-session debug logs, written only when you start with `--debug` or run `/debug`                                                                                                                                                                                                                   |
| `paste-cache/`                                                                                                                  | Contents of large pastes                                                                                                                                                                                                                                                                             |
| `image-cache/<session>/`                                                                                                        | Attached images. On each sweep, Claude Code removes the directories of all other sessions, whatever their age.                                                                                                                                                                                       |
| `uploads/<session>/`                                                                                                            | Files you attach from the web or mobile app, and photos you attach from the mobile app, when messaging a [Remote Control](https://code.claude.com/docs/en/remote-control) session. An attachment to a [cloud session](https://code.claude.com/docs/en/claude-code-on-the-web) is saved in that session's own cloud environment instead, not on your machine. |
| `session-env/`                                                                                                                  | Per-session environment metadata                                                                                                                                                                                                                                                                     |
| `tasks/`                                                                                                                        | Per-session task lists written by the task tools                                                                                                                                                                                                                                                     |
| `shell-snapshots/`                                                                                                              | Aliases, functions, and shell options captured at startup and applied by the [Bash tool](https://code.claude.com/docs/en/tools-reference#bash-tool-behavior) to each command. Removed on clean exit. The sweep clears any left after a crash.                                                                                    |
| `backups/`                                                                                                                      | Earlier versions of `~/.claude.json`, copied when Claude Code rewrites the file. Claude Code keeps the five newest, plus a copy of any version it couldn't parse.                                                                                                                                    |
| `feedback-bundles/`                                                                                                             | Redacted transcript archives written by `/feedback` on third-party providers or when no Anthropic credentials are configured, for sending to your Anthropic account team                                                                                                                             |
| `feedback/drafts/`                                                                                                              | Queued [Claude-drafted feedback](https://code.claude.com/docs/en/tools-reference#sendfeedback-tool-behavior) awaiting your review in `/feedback`. Swept after `cleanupPeriodDays` or 30 days, whichever is shorter. When the queue is at its 10-draft limit, Claude Code deletes the oldest draft to make room.                  |
| `usage-data/`                                                                                                                   | `report.html` and timestamped report copies written by [`/insights`](https://code.claude.com/docs/en/costs#analyze-your-usage-patterns), plus cached per-session analysis data used to build them                                                                                                                                |
| `todos/`, `statsig/`, `logs/`                                                                                                   | Legacy directories from older versions. No longer written. The sweep removes their contents and then the empty directory.                                                                                                                                                                            |

Session files in `sessions/`, auto memory, and Claude Desktop and Cowork transcripts each follow their own retention rule:

* **`sessions/`**: holds one small file per running session, used to detect concurrent sessions and crashes. It isn't part of the age-based sweep: Claude Code removes each file when its session exits and clears crash leftovers on the next launch.
* **Auto memory**: Claude Code excludes a project's [auto memory](https://code.claude.com/docs/en/memory#auto-memory) directory, `projects/<project>/memory/`, from this sweep, and removes the directory itself only after it has been empty for the whole retention period. Before v2.1.228, the sweep treated folders inside the memory directory as session data and could delete old files beneath it.
* **Claude Desktop and Cowork transcripts**: Claude Code keeps the transcript of a session you started or most recently continued in Claude Desktop or Cowork at any age. To give these transcripts an age limit, set [`desktopSessionCleanupPeriodDays`](https://code.claude.com/docs/en/settings-reference#desktopsessioncleanupperioddays). When [managed settings](https://code.claude.com/docs/en/managed-settings) set `cleanupPeriodDays`, Claude Code deletes these transcripts after that period instead. Requires Claude Code v2.1.248 or later; earlier versions delete them after `cleanupPeriodDays`.

Claude Code skips the sweep entirely in these cases:

* **Bare mode**: when you run `claude -p` with [`--bare`](https://code.claude.com/docs/en/headless#start-faster-with-bare-mode), Claude Code doesn't run the sweep in that session.
* **Paused sweep**: if Claude Code can't safely determine the retention period, it pauses the retention cleanup sweep; the [`retention_sweep` event](https://code.claude.com/docs/en/monitoring-usage#retention-sweep-event) lists each configuration that pauses it. When the cause is a settings file that can't be read or parsed, or settings errors with `cleanupPeriodDays` or `desktopSessionCleanupPeriodDays` explicitly set, Claude Code also shows a warning in `/status` until you fix the settings errors. When [managed settings](https://code.claude.com/docs/en/server-managed-settings) provide `cleanupPeriodDays`, Claude Code runs the sweep at the managed value in either case.

### Kept until you delete them

The retention cleanup sweep doesn't cover the following paths. Claude Code keeps them until you delete them, apart from the two caches whose rows say that logging out deletes them.

| Path under `~/.claude/` | Contents                                                                                                                                                                                                                                                                                                                                                          |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `history.jsonl`         | Every prompt you've typed, with timestamp and project path. Used for up-arrow recall.                                                                                                                                                                                                                                                                             |
| `stats-cache.json`      | Aggregated token and cost counts shown by `/usage`                                                                                                                                                                                                                                                                                                                |
| `remote-settings.json`  | Cached copy of [server-managed settings](https://code.claude.com/docs/en/server-managed-settings) for your organization, or `{}` when your organization has configured none. Only present when the session [fetches them](https://code.claude.com/docs/en/server-managed-settings#platform-availability). Claude Code checks for updates at startup and hourly during a session. Claude Code deletes it when you log out. |
| `cache/changelog.md`    | Cached copy of the Claude Code changelog, shown by `/release-notes`. Refreshed in the background.                                                                                                                                                                                                                                                                 |
| `policy-limits.json`    | Cached feature policy settings for your organization. Only present for some account types. Refreshed automatically. Claude Code deletes it when you log out.                                                                                                                                                                                                      |

Other small cache and lock files appear depending on which features you use and are safe to delete.

### Plaintext storage

Transcripts and history are not encrypted at rest. OS file permissions are the only protection. If a tool reads a `.env` file or a command prints a credential, that value is written to `projects/<project>/<session>.jsonl`. To reduce exposure:

* Lower `cleanupPeriodDays` to shorten how long Claude Code keeps transcripts
* Set [`desktopSessionCleanupPeriodDays`](https://code.claude.com/docs/en/settings-reference#desktopsessioncleanupperioddays) to give Claude Desktop and Cowork transcripts an age limit too
* Set the [`CLAUDE_CODE_SKIP_PROMPT_HISTORY`](https://code.claude.com/docs/en/env-vars) environment variable to skip writing transcripts and prompt history in any mode. In non-interactive mode, you can instead pass `--no-session-persistence` alongside `-p`, or set `persistSession: false` in the TypeScript Agent SDK; the Python SDK has no equivalent option.
* Use [permission rules](https://code.claude.com/docs/en/permissions) to deny reads of credential files

### Clear local data

Run `claude project purge` to delete the state Claude Code holds for one project. It deletes:

* Transcripts and auto memory under `projects/`
* Per-session `tasks/`, `debug/`, and `file-history/` entries
* Matching prompt lines in `history.jsonl`
* The project's entry in `~/.claude.json`

The command prints the full deletion plan and asks for confirmation before removing anything.

The examples below use `~/work/my-repo` as a placeholder. Replace it with the path to your project. If no state matches the path, the command prints an error and exits with status 1.

Preview the plan without deleting anything:
```bash
claude project purge ~/work/my-repo --dry-run
```

The plan lists each matching item and why it is included:
```text
Purge plan for /home/user/work/my-repo:

  dir:    /home/user/.claude/projects/-home-user-work-my-repo
           project transcripts (.jsonl) and memory/
  config: projects["/home/user/work/my-repo"]
           project entry in ~/.claude.json (trust, history, MCP servers)
  filter: /home/user/.claude/history.jsonl
           12 prompt(s) typed in this project

shell-snapshots/ are not project-scoped and will not be touched
backups/ may still contain this project entry in old .claude.json snapshots (/home/user/.claude/backups); at most 5 are kept and they rotate out automatically
Dry run: 3 item(s) would be deleted.
```

Delete with a single confirmation prompt:
```bash
claude project purge ~/work/my-repo
```

The command prints the same plan, then asks `Delete 3 item(s) for /home/user/work/my-repo? This cannot be undone. [y/N]` and deletes only if you answer `y`.

Omit the path to pick a project from an interactive list.

Skip the confirmation prompt for use in scripts:
```bash
claude project purge ~/work/my-repo --yes
```

Pass `--all` instead of a path to purge state for every project at once, which deletes `history.jsonl` outright rather than filtering it. Pass `-i` to step through the deletion plan one item at a time.

The command leaves `shell-snapshots/` and `backups/` alone because those are not project-scoped, and warns about them in the plan output.

You can also delete any of the application-data paths above by hand. New sessions are unaffected. The table below shows what you lose for past sessions.

| Delete                                                                                                                                                             | You lose                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `~/.claude/projects/`                                                                                                                                              | Resume, continue, and rewind for past sessions, and auto memory for every project                                 |
| `~/.claude/history.jsonl`                                                                                                                                          | Up-arrow prompt recall                                                                                            |
| `~/.claude/paste-cache/`                                                                                                                                           | Pasted text in recalled prompts; see [paste large content](https://code.claude.com/docs/en/terminal-config#paste-large-content)               |
| `~/.claude/uploads/`                                                                                                                                               | Attachments that past [Remote Control](https://code.claude.com/docs/en/remote-control) sessions refer to by path                              |
| `~/.claude/file-history/`                                                                                                                                          | Checkpoint restore for past sessions                                                                              |
| `~/.claude/stats-cache.json`                                                                                                                                       | Historical totals shown by `/usage`                                                                               |
| `~/.claude/usage-data/`                                                                                                                                            | Past [`/insights`](https://code.claude.com/docs/en/costs#analyze-your-usage-patterns) reports and the cached analysis data used to build them |
| `~/.claude/feedback-bundles/`                                                                                                                                      | Feedback and bug-report archives you haven't yet sent to your Anthropic account team                              |
| `~/.claude/feedback/drafts/`                                                                                                                                       | [Claude-drafted feedback](https://code.claude.com/docs/en/tools-reference#sendfeedback-tool-behavior) you haven't sent                        |
| `~/.claude/remote-settings.json`                                                                                                                                   | Nothing. Re-fetched on next launch.                                                                               |
| `~/.claude/cache/changelog.md`                                                                                                                                     | Nothing. Refreshed in the background.                                                                             |
| `~/.claude/policy-limits.json`                                                                                                                                     | Nothing. Refreshed automatically.                                                                                 |
| `~/.claude/debug/`, `~/.claude/plans/`, `~/.claude/image-cache/`, `~/.claude/session-env/`, `~/.claude/tasks/`, `~/.claude/shell-snapshots/`, `~/.claude/backups/` | Nothing user-facing                                                                                               |
| `~/.claude/todos/`, `~/.claude/statsig/`, `~/.claude/logs/`                                                                                                        | Nothing. Legacy directories not written by current versions.                                                      |

Don't delete `~/.claude.json`, `~/.claude/settings.json`, or `~/.claude/plugins/`: those hold your auth, preferences, and installed plugins.

## Related resources

* [Manage Claude's memory](https://code.claude.com/docs/en/memory): write and organize CLAUDE.md, rules, and auto memory
* [Configure settings](https://code.claude.com/docs/en/settings): set permissions, hooks, environment variables, and model defaults
* [Create skills](https://code.claude.com/docs/en/skills): build reusable prompts and workflows
* [Configure subagents](https://code.claude.com/docs/en/sub-agents): define specialized agents with their own context
