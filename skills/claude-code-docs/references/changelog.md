---
title: Claude Code changelog
source: https://code.claude.com/docs/en/changelog
path: /docs/en/changelog
---

# Claude Code changelog

> Release notes for Claude Code, including new features, improvements, and bug fixes by version.

This page is generated from the [CHANGELOG.md on GitHub](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md).

Run `claude --version` to check your installed version.

### 2.1.176 (June 12, 2026)

* Session titles are now generated in the language of your conversation (set the `language` setting to pin a specific language)
* Added `footerLinksRegexes` setting for regex-matched link badges in the footer row, configurable via user or managed settings
* Improved Bedrock credential caching: credentials from `awsCredentialExport` are now cached until their `Expiration` instead of a fixed 1 hour
* Fixed `availableModels` enforcement: alias model picks can no longer be redirected to a blocked model via `ANTHROPIC_DEFAULT_*_MODEL` environment variables, and `/fast` now refuses to toggle when it would switch to a model outside the allowlist
* Fixed auto mode failing on Fable 5 for organizations without Opus 4.8 enabled — the classifier now falls back to the best available Opus model
* Fixed hook `if` conditions for Read/Edit/Write tool paths: documented patterns like `Edit(src/**)`, `Read(~/.ssh/**)`, and `Read(.env)` now match correctly
* Fixed Linux sandbox failing to start when `.claude/settings.json` is a symlink with an absolute target
* Fixed `/copy` and mouse-selection copy not reaching the system clipboard inside tmux over SSH, and tmux paste buffer not loading on versions older than 3.2
* Fixed Remote Control connecting from web/mobile silently switching the session's model
* Fixed Remote Control disconnect notifications showing a bare numeric code instead of a human-readable reason, and connection failures adding a duplicate line to the conversation transcript
* Fixed Remote Control sessions not disconnecting when you sign in to a different account
* Fixed `/cd` and worktree moves leaving the session reporting the previous directory's git branch
* Fixed `claude agents`: pressing back in one window no longer detaches other windows attached to the same session
* Fixed backgrounded sessions showing "Working" forever when `/bg` mid-turn had nothing left to continue
* Fixed background agent search by PR URL: PRs opened during scheduled wakeups or while a job was blocked now appear in `claude agents` search
* Fixed the agents view input showing no text cursor on Windows
* Fixed `claude --bg -cn <name>` not seeding the session name
* Fixed background sessions to neutralize Windows network paths in persisted state before respawn
* Fixed background-session respawn rejecting malformed resume IDs from corrupted state files
* Fixed the Windows background-service daemon not starting when `~/.claude/daemon` has the ReadOnly attribute set
* Fixed cloud sessions failing with "Could not resolve authentication method" when idle for too long before being claimed
* Background sessions now show clearer guidance when a window left open across an auto-update can't submit a reply, and `claude daemon status` explains version-skew behavior

### 2.1.175 (June 12, 2026)

* Added `enforceAvailableModels` managed setting — when enabled, the `availableModels` allowlist also constrains the Default model (a Default that would resolve to a disallowed model now falls back to the first allowed model), and user or project settings can no longer widen a managed `availableModels` list

### 2.1.174 (June 12, 2026)

* Added `wheelScrollAccelerationEnabled` setting to disable mouse-wheel scroll acceleration in fullscreen mode
* Fixed the `/model` picker hiding the model family that Default resolves to — Opus now appears as its own row on Max/Team Premium/Enterprise plans, Sonnet on Pro/Team plans, and Opus on pay-as-you-go API accounts
* Fixed `/model` picker showing a hardcoded Sonnet version label when `ANTHROPIC_DEFAULT_SONNET_MODEL` pins a different Sonnet
* Fixed the "Fable 5 is now consuming usage credits" banner incorrectly showing for enterprise accounts with usage-based billing
* Fixed Bedrock GovCloud regions (`us-gov-*`) deriving the wrong inference profile prefix (`global` instead of `us-gov`), causing 400 errors on derived model IDs
* Fixed background sessions inheriting another session's `ANTHROPIC_*` provider env (gateway URL, custom headers, `/model` aliases) from the shell that started the background daemon
* Fixed a 1-2 second pause when exiting Claude Code shortly after a shell command was interrupted or killed on macOS and Linux
* Fixed git commit co-author attribution showing an incorrect model name for some models
* Fixed the `/advisor` dialog pre-selecting a saved advisor model that is blocked by the `availableModels` allowlist
* Fixed skill hot-reload re-sending the entire skill listing when a single skill changed; only changed skills are now re-announced
* Fixed Workflow tool `agent()` subagents missing per-agent attribution headers
* \[VSCode] Added usage attribution to the Account & usage dialog (`/usage`) showing cache misses, long context, subagents, and per-skill/agent/plugin/MCP breakdowns over the last 24h or 7d
* Fixed pre-warmed background workers failing with "Could not resolve authentication method" when claimed after sitting idle

### 2.1.173 (June 11, 2026)

* Fixed Fable 5 model names with a `[1m]` suffix not being normalized — Fable 5 includes 1M context by default, so the suffix is now stripped automatically
* Fixed a spurious "sandbox dependencies missing" startup warning on Windows when sandbox was enabled in settings

### 2.1.172 (June 10, 2026)

* Sub-agents can now spawn their own sub-agents (up to 5 levels deep)
* Amazon Bedrock now reads the AWS region from `~/.aws` config files when `AWS_REGION` isn't set, matching AWS SDK precedence; `/status` shows where the region came from
* Added a search bar when browsing a marketplace's plugins in `/plugin`
* Added `model` attribute to the `claude_code.lines_of_code.count` OTEL metric
* Fixed sessions using 1M context without usage credits getting permanently stuck — the session now automatically compacts back under the standard context limit
* Fixed a repeating "an image in the conversation could not be processed and was removed" error when the conversation contained multiple images
* Fixed the agents view keeping a session under Working with a busy spinner for up to 30 seconds after the worker replied
* Fixed background agents potentially reading another directory's project settings (`.mcp.json` approvals, trust) when dispatched onto a pre-warmed worker
* Fixed background-session attach failing with EAUTH for sessions started on an older version after the daemon auto-updated
* Fixed a background sub-agent staying stuck as "active" in the agent panel after a nested agent it spawned was stopped
* Fixed `/model` suggestions in the `claude agents` dispatch input rendering with a misleading slash prefix and showing models disabled for your org
* Fixed `availableModels` restrictions not being applied to subagent model overrides, the agent dispatch model picker, and the advisor model
* Fixed `availableModels` allowlists hiding the `/model` picker's Opus and Sonnet 1M rows when entries use version-specific IDs like `claude-opus-4-8`
* Fixed the `/model` picker on Bedrock offering models the provider doesn't serve — selecting one silently switched the session model and lit the selection marker on multiple rows
* Fixed model IDs getting a doubled 1M-context suffix (e.g. `[1M][1m]`) when `ANTHROPIC_DEFAULT_OPUS_MODEL` already includes one
* Fixed `opusplan` model setting not shipping with 1M context in plan mode for entitled users; the `opusplan[1m]` workaround now also correctly switches to Opus in plan mode
* Fixed `WebFetch(domain:*.example.com)` wildcard domain rules never matching subdomains in allow, deny, and ask position, and file permission rules with mid-pattern wildcards (e.g. `Read(secrets-*/config.json)`) being rejected at startup
* Fixed up-arrow prompt history showing the main agent's prompts while a subagent's chat tab is open
* Fixed memory recall not finding mounted team memory stores (`CLAUDE_MEMORY_STORES`) in remote sessions
* Fixed workflow validation rejecting scripts whose prompt strings or comments merely mention `Date.now()`/`Math.random()`
* Disable mouse tracking on Windows consoles that don't fully support it
* Fixed the `/plugin` marketplace list losing its cursor after backing out of a long plugin list, and Esc from the plugin browser returning to the wrong tab
* Improved performance in long conversations by removing redundant message normalization and avoiding full message-history transforms when streaming tool-use state is unchanged
* Reduced idle CPU usage: `/goal` status chip no longer re-renders the terminal at 5 Hz while idle, and fewer UI re-renders while subagents run in parallel
* Improved Claude in Chrome tool loading: browser tools now load in a single batched call instead of one per tool
* Improved the non-interactive Usage Policy refusal message to suggest starting a new session or changing your model
* `/code-review` now keeps the `ultra` option visible when you're not signed in to claude.ai, with an explanation that the cloud review requires a claude.ai account
* Shortened the Remote Control footer indicator to "/rc active" and hid it on narrow terminals
* Stopped promoting `/loop` in remote sessions, where pending loops don't keep the container alive
* \[VSCode] Fixed PowerShell tool calls rendering as raw JSON instead of a proper command display and permission dialog, and stripped ANSI escape codes from displayed shell output

### 2.1.170 (June 9, 2026)

* Introducing Claude Fable 5: a Mythos-class model that we’ve made safe for general use. Fable’s capabilities exceed those of any model we’ve ever made generally available. Update to version 2.1.170 for access. [https://www.anthropic.com/news/claude-fable-5-mythos-5](https://www.anthropic.com/news/claude-fable-5-mythos-5)
* Fixed sessions not saving transcripts (and not appearing in --resume) when launched from the VS Code integrated terminal or any shell that inherited Claude Code environment variables.

### 2.1.169 (June 8, 2026)

* Self-hosted runner: added a `post-session` lifecycle hook that runs after the session ends and before the workspace is deleted, so you can snapshot uncommitted work or export logs; also made the child-process SIGTERM→SIGKILL window configurable (default unchanged at 5s)
* Added `--safe-mode` flag (and `CLAUDE_CODE_SAFE_MODE`) to start Claude Code with all customizations (CLAUDE.md, plugins, skills, hooks, MCP servers) disabled for troubleshooting
* Added `/cd` command to move a session to a new working directory without breaking the prompt cache mid-session
* Added a `disableBundledSkills` setting and `CLAUDE_CODE_DISABLE_BUNDLED_SKILLS` environment variable to hide bundled skills, workflows, and built-in slash commands from the model
* Fixed Up/Down arrows jumping to command history past the wrapped rows of a long input line — they now move through each visual row first, and history recall enters at the near edge
* Fixed enterprise managed MCP policies (`allowedMcpServers`/`deniedMcpServers`) not being enforced on reconnect, IDE-typed configs, `--mcp-config` servers during the first session after install, or before remote settings loaded; also fixed slow cold starts for orgs without remote settings
* Fixed a \~30-50ms UI stall at the start of each turn for macOS users logged in with claude.ai credentials
* Fixed `claude -p` being slow or appearing to hang on Windows while waiting for the slash-command/skill scan (regression in 2.1.161)
* Fixed Remote Control getting stuck on "reconnecting" after resuming a session when an OAuth token refresh happened at the same time
* Fixed Git Credential Manager's "Connect to GitHub" popup appearing on Windows at startup when background git commands ran without cached credentials
* Fixed footer hints (e.g. "esc to interrupt") not showing for users with a custom statusline
* Fixed stale permission and dialog prompts reappearing every time you reattached to a remote session whose worker had died while waiting on them
* Fixed `claude agents --json` omitting blocked and just-dispatched background sessions; added `--all` to include completed sessions, plus new `id` and `state` fields
* Fixed agents view leaving a stale/garbled frame after navigating back from an agent on WSL in Windows Terminal
* Fixed background agents ignoring project-level settings `env` values (e.g. `ANTHROPIC_MODEL`) when dispatched onto a pre-warmed worker
* Fixed MCPB plugin cache being spuriously invalidated on Windows, causing unnecessary re-extraction
* Fixed plugin `.in_use` PID lock files accumulating without bound; stale markers from crashed sessions are now swept once per day
* Fixed untrusted project settings being able to set OTEL client-certificate paths without trust confirmation
* `/workflows` now opens immediately even while a turn is in progress
* Improved `TaskCreate` reliability: malformed inputs are repaired automatically and validation errors for unloaded tools include the schema
* Improved the error message shown when your organization has disabled API key authentication, with guidance based on where the active API key comes from
* Reduced CPU usage while responses stream and during spinner animations
* Restored a default 5-minute idle timeout on Vertex/Foundry so a stalled stream aborts instead of hanging indefinitely; set `API_FORCE_IDLE_TIMEOUT=0` to opt out
* Remote-managed settings with an invalid entry now apply their remaining valid policies and surface the validation error, instead of silently dropping the whole payload
* Background sessions now preserve `--ide`, `--chrome`, `--bare`, `--remote-control`, and other flags across retire→wake, and respawn state validation was hardened
* Background sessions are now told that shared-checkout edits are blocked until they enter a worktree, avoiding a wasted rejected edit before `EnterWorktree`
* The "CLAUDE.md is too long" warning threshold now scales with the model's context window
* Auto-updater on Windows now stops retrying within a session once `claude.exe` is held by another process
* Improved color contrast for skill tags in the slash-command menu
* Promo credit claims for Apple/Google-billed subscribers without a payment method now explain where to add one
* Added a tip suggesting `claude agents` when running multiple concurrent sessions

### 2.1.168 (June 6, 2026)

* Bug fixes and reliability improvements

### 2.1.167 (June 6, 2026)

* Bug fixes and reliability improvements

### 2.1.166 (June 6, 2026)

* Added `fallbackModel` setting to configure up to three fallback models tried in order when the primary model is overloaded or unavailable; `--fallback-model` now also applies to interactive sessions
* Added glob pattern support in deny rule tool-name position (`"*"` denies all tools); allow rules reject non-MCP globs, and unknown tool names in deny rules warn at startup
* Hardened cross-session messaging: messages relayed via `SendMessage` from other Claude sessions no longer carry user authority — receivers refuse relayed permission requests, and auto mode blocks them
* `MAX_THINKING_TOKENS=0`, `--thinking disabled`, and the per-model thinking toggle now disable thinking on models that think by default via the Claude API (3P providers unchanged)
* Claude Code now retries a turn once on the fallback model when the API rejects an unexpected non-retryable error; auth, rate-limit, request-size, and transport errors still surface immediately
* `claude update` now announces the target version before downloading instead of going silent
* `claude agents`: typing a URL into the list now filters to the session whose first prompt contained it
* Fixed a recurring "image could not be processed" error and extra token usage when an unprocessable image was sent in a session
* Fixed remote sessions becoming permanently stuck when a brief backend disruption occurred during worker registration at startup
* Fixed flickering in JetBrains IDE terminals (IntelliJ, PyCharm, WebStorm, etc.) on 2026.1+ by enabling synchronized output
* Fixed Shift+non-ASCII characters (e.g. Shift+ä → Ä) being dropped in terminals using the Kitty keyboard protocol (WezTerm, Ghostty, kitty)
* Fixed PowerShell command validation occasionally hanging far past its time budget on Windows when a killed process's children held its output pipes
* Fixed orphaned `claude --bg-pty-host` processes spinning at 100% CPU after the daemon dies while connected on macOS
* Fixed voice mode requiring `/login` to clear a stale auth check after toggling `/voice`
* Fixed managed settings with an invalid entry silently disabling enforcement of their remaining valid policies
* Fixed managed-settings `allowedMcpServers`/`deniedMcpServers` predicates not matching when they use `${VAR}` references
* Fixed background agent sessions that entered a git worktree crash-looping with "No conversation found" when reopened from `claude agents`
* Fixed duplicated thinking text in the Ctrl+O transcript view while streaming
* Fixed `/doctor` showing a contradictory failed "Not inside a remote session" check when run inside a remote session
* Fixed the cursor sticking at the end of the first line when typing a multiline prompt in the `claude agents` dispatch and reply inputs
* Fixed blank lines appearing between background agent rows in the task list on terminals without Unicode support

### 2.1.165 (June 5, 2026)

* Bug fixes and reliability improvements

### 2.1.163 (June 4, 2026)

* Added `requiredMinimumVersion` and `requiredMaximumVersion` managed settings — Claude Code refuses to start if its version is outside the allowed range and directs the user to an approved version
* Added `/plugin list` command to list installed plugins, with `--enabled`/`--disabled` filters
* Added a "c to copy" shortcut to `/btw` that copies the raw markdown answer to the clipboard, preserving formatting when pasted elsewhere
* Hooks: Stop and SubagentStop hooks can now return `hookSpecificOutput.additionalContext` to give Claude feedback and keep the turn going without being labeled a hook error
* Skills: added `\$` escape syntax to include a literal `$` before a digit in command bodies
* stdio MCP servers now receive the same `CLAUDE_CODE_SESSION_ID` as hooks/Bash on `--resume`
* Fixed `claude -p` hanging forever after its final result when a backgrounded command never exits — background shells are now stopped \~5s after the result once stdin closes
* Fixed `claude -p` failing with "ANTHROPIC\_API\_KEY required" on Bedrock/Vertex/Foundry when `CI=true` and no Anthropic API key is set
* Fixed bash commands failing under bazel and EDR-protected Go workflows: `$TMPDIR` was overridden to `/tmp/claude-{uid}` for all commands instead of only sandboxed ones (regression in 2.1.154)
* Fixed Bash commands failing on Windows with "EEXIST: file already exists" on the session-env directory when it has the read-only attribute or is inside OneDrive
* Fixed org-managed permission rules not applying for the entire session when the managed settings fetch completed during startup on a fresh config directory
* Fixed background sessions in `claude agents` losing their running background tasks when reattached after a Claude Code update
* Fixed terminal misalignment and a multi-second hang when exiting the agent view by pressing Esc
* Fixed clicking Stop on a background-task chip in the desktop app not clearing the chip when the underlying process was already gone
* Fixed keyboard input becoming permanently unresponsive after a paste operation whose end marker is dropped by the terminal
* Fixed hook `if: "Bash(...)"` conditions firing on every Bash command containing `$()` or `$VAR`; the pattern now matches against commands inside subshells and backticks too
* Fixed deny rules on home-directory paths (e.g. `Read(~/Desktop/**)`) not blocking Bash commands that reference the path via `$HOME`
* Fixed a stray "(no content)" line left in the transcript after closing panel dialogs like /mcp and /plugins
* Background agent sessions now update to a new Claude Code version in the background, so opening a session after an update no longer waits on a cold restart
* Clearer descriptions for built-in commands and skills in the / menu
* The subscription-switch suggestion now shows in the startup announcement slot instead of a toast
* `claude agents` dispatching from the state-grouped view now starts the session in the directory the agent view was opened from

### 2.1.162 (June 3, 2026)

* `claude agents --json` now includes `waitingFor` showing what a waiting session is blocked on (e.g. permission prompt)
* `--tools`: explicitly listing Grep/Glob now provides the dedicated search tools on native builds with embedded search (previously these names were silently ignored)
* `/effort` now confirms when your chosen level will persist as the default for new sessions
* Clicking a slash command in the autocomplete menu now fills it into your prompt instead of running it immediately; press Enter to run
* Remote Control now shows as a persistent footer pill (with a link to the session) instead of a startup message
* Renamed Windsurf to Devin Desktop in the `/ide` menu, `/terminal-setup`, and `/scroll-speed`, following the editor's rebrand
* Fixed a silent startup hang when the config directory is read-only or unwritable — Claude Code now starts with in-memory config and surfaces startup errors instead of showing a blank screen
* Fixed WebFetch permission rules not being applied to built-in preapproved domains; explicit `WebFetch(domain:...)` deny/ask/allow rules now take precedence over the preapproved-host auto-allow
* Fixed Windows permission rules never matching when spelled with backslashes (`~\`, `\\server\share`) or case-variant paths, and Read deny rules not hiding files from Glob/Grep results
* Fixed an interrupt (Esc) sent at the very start of a turn being silently dropped in stream-json/SDK sessions, leaving the turn running with no "Interrupted" feedback
* Fixed API 400 `no low surrogate in string` errors for classifier side-queries and MCP server descriptions containing emoji near a truncation boundary
* Fixed MCP per-server `timeout` config values below 1000 ms being floored to a 1-second watchdog that aborted every tool call; sub-1000 ms values are now ignored (falling back to `MCP_TOOL_TIMEOUT` or default), and `claude mcp get` annotates them accordingly
* Fixed the LSP tool's `workspaceSymbol` operation returning no results; it now accepts a `query` parameter and passes it to the language server
* Fixed `claude agents` cutting live status text (tool args, replies, prompts, exec output) at 60–120 columns on wide terminals; the status detail now uses the full terminal width
* Fixed `claude agents` truncating long session names at 40 columns; the name column now grows with terminal width
* Fixed `claude agents` attach occasionally bouncing straight back to the session list on the first try after a background-service restart
* Fixed `claude agents` Ctrl+V image paste doing nothing in the dispatch input and the session reply box; pasting with no image now shows a hint
* Fixed backgrounding a session with ← silently losing the conversation when the background service cannot start; the session stays in the list as a failed row you can wake with Enter
* Fixed replies from the agents view that fail to send being lost; they are now queued for delivery on the next session start
* Fixed cross-session messaging (`SendMessage`) silently breaking when `CLAUDE_CODE_TMPDIR` or `$TMPDIR` points at a deep directory
* Fixed opening a running background session from `claude agents` stalling for 5 seconds before attaching
* Quieter startup: notices group by severity, and session info and announcements share a single line per launch
* Startup warnings rewritten to be shorter and clearer, each with a concrete fix
* Launch-prompt warnings (deep link/pre-filled prompt) now stay pinned below the input until you act instead of scrolling away
* Failed turns now show a compact warning line instead of a multi-line red error block
* Improved background service startup and `claude update` verification to wait out endpoint-security scanning of new binaries instead of failing after 5 seconds
* Background dispatch spawn failures now report the error class name when no errno is available
* Removed the "Claude in Chrome enabled" and "marketplace installed" startup messages; model auto-updates and the team-onboarding tip now show as quiet notices under the logo

### 2.1.161 (June 2, 2026)

* `OTEL_RESOURCE_ATTRIBUTES` values are now included as labels on metric datapoints, so you can slice usage metrics by custom dimensions like team or repo
* `claude agents` rows now show `done/total` before the detail when work is fanned out; peek shows the longest-running item
* `/mcp` now collapses claude.ai connectors you've never signed in to behind a "Show unused connectors" row
* Parallel tool calls: a failed Bash command no longer cancels other calls in the same batch — each tool returns its own result independently
* Fullscreen mode: clipboard now uses `wl-copy`/`xclip`/`xsel` on Linux when available, copies to both the clipboard and PRIMARY selection for middle-click paste, and the "hold `{key}` for native selection" hint now shows the correct key per terminal
* Fixed the `/effort` dialog, workflow animations, and prompt keyword shimmer not honoring the "Reduce motion" setting
* Fixed `forceLoginOrgUUID`/`forceLoginMethod` managed-settings policies blocking third-party provider sessions (Bedrock, Vertex, Foundry, Mantle) alongside the org pin (regression in 2.1.146)
* Fixed background subagent output corrupting `claude -p` stdout when using `--output-format text` or `json`
* Fixed `/usage-credits` starting a re-login for Team and Enterprise admins instead of pointing to the organization's usage settings page
* Fixed `/autofix-pr` reporting "cannot run on the default branch" when the session is inside a git worktree or another repository
* Fixed `--resume` picker not showing sessions from the current directory when it isn't a git worktree (e.g., jj workspaces)
* Fixed Windows hooks that invoke bash explicitly (e.g., `/usr/bin/bash script.sh`) failing with "command not found" or "cannot execute binary file"
* Fixed OpenTelemetry log events (`user_prompt`, `api_request`, `tool_result`, `tool_decision`) being silently dropped when emitted before telemetry initialization completed
* Fixed `claude mcp` list/get/add printing secrets to the terminal: `${VAR}` references are no longer expanded, and credential headers and URL secrets are redacted
* Fixed Workflow agents spawned with `isolation: "worktree"` in background sessions being blocked from editing files inside their own worktree
* Fixed background sessions dispatched from `claude agents` booting on a stale model from the daemon's environment instead of the model in `settings.json`
* Fixed a potential crash when rendering Write tool results after resuming a session
* Fixed completed subagents getting stuck showing as running when an error occurs while finalizing their result
* Fixed `EADDRINUSE` errors from tools that bind Unix sockets under `$TMPDIR` when `CLAUDE_CODE_TMPDIR` is set to a deep path
* Improved terminal rendering performance by stabilizing the layout engine's JIT compilation profile
* Improved rendering performance for large file writes
* \[VSCode] Added a tip suggesting disabling terminal GPU acceleration (or running `/terminal-setup`) to fix garbled glyphs

### 2.1.160 (June 2, 2026)

* Added a prompt before writing to shell startup files (`.zshenv`, `.zlogin`, `.bash_login`) and `~/.config/git/`, which could otherwise lead to unintended command execution
* `acceptEdits` mode now prompts before writing build-tool config files that grant code execution (`.npmrc`, `.yarnrc*`, `bunfig.toml`, `.bazelrc`, `.pre-commit-config.yaml`, `.devcontainer/`, etc.)
* Edit no longer requires a separate Read after viewing a file with `grep`: single-file `grep`/`egrep`/`fgrep` commands now satisfy the read-before-edit check
* Fixed copy-on-select not writing to the Windows clipboard on WSL — now uses PowerShell interop instead of OSC 52, which terminals like MobaXterm don't support
* Fixed restoring a completed session from `claude agents` dropping chat history and re-running the original prompt
* Fixed background sessions re-attached after overnight retire losing their conversation and re-running the original prompt
* Fixed `claude --bg` occasionally failing with "socket missing" when the background daemon was cold-starting on a loaded machine
* Fixed an issue on Windows where the directory a background session was started in could not be deleted after `claude rm` until the background daemon exited
* Fixed background agents that resumed work being shown under Completed in the agents list
* Fixed `claude agents` freezing for several seconds when returning to the session list due to the auto-updater re-checking on every exit
* Fixed Esc, arrow keys, and typing becoming unresponsive on Windows when attached to a background session or in the agent view while the host is under heavy CPU load
* Fixed background agents emitting terminal sync-output markers to terminals that don't support them (Apple Terminal, tmux), causing render artifacts when entering a running agent
* Fixed mouse wheel scrolling prompt history instead of the transcript right after opening a session from the agents list
* Fixed CJK IME composition appearing at the bottom-left of the screen instead of at the input caret in the `claude agents` view
* Fixed valid `file:///C:/...` links being rewritten to a broken path on Windows terminals with hyperlink support
* Fixed voice mode failing to connect when the project directory or branch name contains non-ASCII or special characters
* Fixed the auto mode unavailability message on third-party providers (Bedrock/Vertex/Foundry) to point to the `CLAUDE_CODE_ENABLE_AUTO_MODE` opt-in instead of incorrectly blaming the model
* Fixed `/effort ultracode` incorrectly blaming the dynamic workflows setting when the model cannot run xhigh; ultracode is no longer offered on models that do not support it
* Fixed model-not-found errors suggesting `--model` when running via the SDK or other hosts where the CLI flag doesn't apply
* Fixed Claude's past replies disappearing from scrollback when resuming a brief mode session with brief mode turned off
* Fixed vim mode `p` pasting on the line below instead of at the cursor when the register was yanked with `v$`
* Improved performance of opening recently-inactive background agent sessions in `claude agents`
* Improved auto mode classifier latency by reducing reasoning on routine actions, lowering the chance of "could not evaluate this action" blocks
* Improved background-session teardown (`claude rm`/`stop`, idle reap) to send SIGTERM to running shell subprocesses before SIGKILL, so cleanup handlers run
* Removed `CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE`; the environment variable is now a no-op
* Removed the JetBrains plugin install suggestion from startup
* Renamed the dynamic-workflow trigger keyword from `workflow` to `ultracode`. The word "workflow" no longer triggers a run; asking for one in your own words still works. The trigger keyword is highlighted in violet in the prompt input

### 2.1.159 (May 31, 2026)

* Internal infrastructure improvements (no user-facing changes)

### 2.1.158 (May 30, 2026)

* Auto mode is now available on Bedrock, Vertex, and Foundry for Opus 4.7 and Opus 4.8. Opt in by setting `CLAUDE_CODE_ENABLE_AUTO_MODE=1`

### 2.1.157 (May 29, 2026)

* Plugins in `.claude/skills` directories are now automatically loaded, no marketplace required
* Added `claude plugin init <name>` to scaffold a new plugin in `.claude/skills`
* Added autocomplete for `/plugin` arguments: subcommands, installed plugin names, and plugins from known marketplaces
* `claude agents`: the `agent` field in `settings.json` is now honored for dispatched sessions, with `--agent <name>` to override it
* `EnterWorktree` can now switch between Claude-managed worktrees mid-session
* `tool_decision` telemetry events now include `tool_parameters` (bash commands, MCP/skill names) when `OTEL_LOG_TOOL_DETAILS=1`
* Worktrees managed by Claude are now left unlocked when the agent finishes, so `git worktree remove`/`prune` can clean them up
* Fixed unprocessable images (zero-byte, corrupt) attached via paste, MCP, or dialog crashing the request instead of becoming a text placeholder
* Fixed sandbox network permission prompts appearing in auto and bypass-permissions mode when using the desktop app, IDE extensions, or SDK
* Fixed `claude agents` completed sessions not retiring when an idle subagent was still parked or had leaked a backgrounded shell
* Fixed `claude agents` pressing Esc not cancelling a slow "opening…", leaving the list unresponsive
* Fixed background agent worktrees under `.claude/worktrees/` being orphaned after the 30-day job retention sweep
* Fixed background sessions re-attached after a sleep/wake not telling the model the correct date
* Fixed copy-on-select in `claude agents` not reaching the system clipboard inside tmux with `set-clipboard on` (regression in 2.1.153)
* Fixed `--resume` not reporting background subagents that were running when the previous Claude Code process exited
* Fixed the `--resume` session picker leaving its contents on the terminal after exiting in fullscreen mode
* Fixed `--worktree` and `--worktree --tmux` returning to the canonical repo root instead of the current linked worktree
* Fixed the `/model` picker showing an incorrect "Newer version available" hint when the selected model is already the newest in its family; the pinned-model row now shows the model's description instead of its raw ID
* Fixed literal markdown markers (backticks, asterisks) appearing in the in-progress message text in fullscreen mode
* Fixed the terminal freezing after approving the managed-settings security dialog at startup
* Fixed a rare duplicate line appearing in scrollback after the terminal UI redraws
* Fixed right-click paste duplicating the clipboard in the VS Code, Cursor, and Windsurf integrated terminals
* WSL: fixed image paste (`alt+v` keybinding), screenshot paste on Windows 11, and added support for dragging images from Windows Explorer
* Improved performance of long and resumed conversations by eliminating redundant message-rendering recomputations
* `/terminal-setup` now disables GPU acceleration in VS Code/Cursor/Windsurf integrated terminals to prevent garbled-text rendering
* The Feature of the Week credit-claim status now appears as a notification in the status area instead of a line above the prompt
* `claude agents`: slash-command autocomplete in the dispatch input now matches substrings
* Removed the "bash commands will be sandboxed" startup banner — sandbox status still shows in `/status` and when a command is blocked
* Removed the "/ide for …" startup hint toast
* \[IDE] Fixed clicking Stop while a background subagent is running not actually stopping it
* \[VSCode] Fixed the fast mode indicator not appearing on Opus 4.8
* Pressing backspace right after a workflow trigger keyword now dismisses the workflow request (same as alt+w) instead of deleting a character
* Added a "Workflow keyword trigger" setting in /config to stop the word "workflow" in a prompt from triggering a dynamic workflow

### 2.1.156 (May 29, 2026)

* Fixed an issue when using Opus 4.8 where thinking blocks were modified, leading to API errors.

### 2.1.154 (May 28, 2026)

* Opus 4.8 is here! Now defaults to high effort · /effort xhigh for your hardest tasks
* Introducing dynamic workflows: ask Claude to create a workflow and it orchestrates work across tens to hundreds of agents in the background, so you can take on larger, more complex tasks. Run `/workflows` to view your runs
* Fast mode on Opus 4.8 is now available at a fraction of its previous cost: 2x the standard rate for 2.5x the speed
* The lean system prompt is now the default for all models except Haiku, Sonnet, and Opus 4.7 and earlier
* Claude now reserves the multiple-choice question prompt for decisions it genuinely cannot make itself, instead of asking when it already has enough context to proceed
* `/simplify` now runs a cleanup-only review (reuse, simplification, efficiency, altitude) and applies the fixes, instead of running the full `/code-review --fix` bug-hunting review
* Renamed the `/effort` slider labels from "Speed"/"Intelligence" to "Faster"/"Smarter" for clarity
* `claude agents`: type `! <command>` to run a shell command as a background session you can attach to and detach from. Also available as `claude --bg --exec '<command>'`
* `claude agents`: `/logout` now signs you out instead of being sent to a background session
* `←←` to open the agents view now works on Bedrock, Vertex, Foundry, and with telemetry disabled
* Claude in Chrome: pick which connected browser to use via `/chrome` → "Select browser…", or in-chat when a browser action runs with multiple connected
* Plugins can now declare `defaultEnabled: false` in `plugin.json` or a marketplace entry; enable them with `/plugin` or `claude plugin enable`. Dependencies of enabled plugins are still enabled automatically
* The `/plugin` Discover tab now pins plugins whose relevance signals match the current directory with a "suggested for this directory" annotation
* Streaming tool execution is now always enabled, including when telemetry is disabled or on Bedrock/Vertex/Foundry (previously behind a feature flag)
* Stdio MCP server subprocesses now receive `CLAUDE_CODE_SESSION_ID` and `CLAUDECODE=1` in their environment
* `claude mcp list`/`get` now show unapproved `.mcp.json` servers as `⏸ Pending approval` instead of auto-approving and connecting when output is piped
* `/remote-control` autocomplete now shows "Disconnect Remote Control" when Remote Control is already active
* Added Claude Opus 4.8 support and 4.7 → 4.8 migration guidance to the `/claude-api` skill
* Deprecated `CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE` (will be removed on 06/01). To use fast mode on Opus 4.6, switch with `/model claude-opus-4-6[1m]` and then `/fast on`
* Improved the auto-mode classifier's detection of data exfiltration, particularly bulk transfers of repository contents
* Fixed `rm -rf $HOME` not being blocked as a dangerous path when `HOME` has a trailing slash
* Fixed `$TMPDIR` resolving to different directories in sandboxed vs unsandboxed Bash commands within the same session
* Fixed unreadable highlighted-row text in `claude agents` when the Claude Code theme doesn't match the terminal background
* Fixed background-agent completion notifications triggering premature "out of context" behavior on some 1M-context models
* Fixed background-session classifier losing the user's goal when a scheduled `/command` fires
* Fixed pinned background sessions respawning every minute after a Claude Code update, causing repeated agent-start notifications and process churn at idle
* Fixed background sessions stuck at "blocked", "running", or "working" not retiring after the idle grace period
* Fixed subagents in background sessions bypassing the worktree-isolation guard and writing to the shared checkout
* Fixed orphaned `claude --bg-pty-host` processes spinning at 100% CPU after the daemon exits on macOS
* Fixed number key shortcuts not working for options shown below the divider in option dialogs
* Fixed `worktree.baseRef: "head"` resolving to the main checkout's HEAD instead of the current worktree's HEAD when spawning subagents or calling `EnterWorktree` from inside a linked worktree
* Fixed a stray leading space on wrapped lines when the previous line ended exactly at the terminal width
* Fixed intermittent terminal rendering corruption in VS Code by capping the number of distinct colors the thinking spinner produces
* Fixed plan file names including `[Image #N]` / `[Pasted text #N]` placeholders when a plan-mode prompt starts with pasted images or text
* Fixed a phantom expand/click affordance on colored tool output: short ANSI-colored lines that fit on screen no longer show a "ctrl+o to expand" hint
* Fixed a single invalid `allowedMcpServers`/`deniedMcpServers` entry in managed settings discarding all managed-settings policy; the bad entry is now dropped with a `claude doctor` warning
* Fixed API 400 errors on models that don't support the effort parameter when `CLAUDE_CODE_ALWAYS_ENABLE_EFFORT` is set
* Windows: Fixed update failures caused by `claude.exe` being in use showing a generic error instead of telling you to close other sessions and retry
* Removed the stale "& for background" hint from the shortcuts help panel
* \[VSCode] Auto mode no longer requires the bypass-permissions setting to appear in the mode picker, and a dismissable notice on the new-session screen explains auto mode the first time it's active
* Fixed the task panel below the prompt showing a stray unselectable "main" row when only a workflow is running
* Fixed /mcp tools list and tool detail rendering when MCP servers have long or multi-line tool names or long descriptions
* Fixed the /model picker not showing fast mode pricing on the Default option for API (pay-as-you-go) users when fast mode is on
* Fixed auto mode incorrectly blocking actions with "could not evaluate this action" when the safety classifier ran out of output tokens while reasoning

### 2.1.153 (May 28, 2026)

* Added `skipLfs` option to `github`/`git` plugin marketplace sources to skip Git LFS downloads during clone and update
* Claude Code now shows a one-time notice when your npm global install can't auto-update; `/doctor` lists the fixes
* Status line commands now receive `COLUMNS` and `LINES` environment variables so scripts can size output to the terminal width
* `claude agents`: autocomplete in the dispatch input now suggests native slash commands and bundled skills, not just project skills
* `claude agents`: PR column now shows `PR #N` for a single PR or `N PRs` for multiple
* `claude doctor` now shows the result of your last update attempt
* Combined the separate "needs authentication" startup notifications for MCP servers and connectors into a single message
* macOS: background agents now appear as "Claude Code" in Privacy & Security and keep their permission grants across upgrades
* Fixed stateful MCP servers without the optional GET SSE stream reconnect-looping on `tools/list` (regression in v2.1.147)
* Fixed a regression where a custom API gateway could receive the user's Anthropic OAuth credential instead of the gateway's own token
* Fixed subagent (Agent tool) frontmatter MCP servers ignoring `--strict-mcp-config`, `--bare`, remote mode, enterprise managed MCP config, and managed-settings MCP server allow/deny policies
* `--strict-mcp-config` no longer strips inline `mcpServers` from explicitly-passed agent definitions (`--agents` / SDK `agents`), and blocked subagent MCP servers now surface a visible warning
* Fixed the Windows PowerShell installer reporting "Installation complete!" when installation actually failed
* Fixed `claude update` installing the latest version instead of the configured release channel's version for npm installations
* Fixed excessive memory usage (multiple GB) when resuming a session by transcript file path on machines with many stored sessions
* Fixed `claude agents` and `claude --bg` running on a stale daemon started before binary-takeover support, even after upgrading
* Fixed a hang where the CLI could fail to exit when stdin was closed without EOF in stream-json mode, leaving a stale session marker behind
* Fixed malformed `file://` links in Claude's responses not being clickable in the terminal
* Fixed `claude --help` rendering unwrapped output on terminals narrower than 92 columns
* Fixed MCP tool progress notifications not rendering in the collapsed tool view
* Fixed `Agent` tool with `subagent_type: 'claude'` running in an undocumented temporary worktree, which could silently discard outputs written to gitignored paths
* `/bg` while Claude is responding now continues the response in the background session instead of dropping it
* Fixed `/btw` keyboard shortcuts becoming unresponsive in background sessions while a task is running
* Fixed background sessions writing temp files to `$CLAUDE_JOB_DIR` triggering a "sensitive file" permission prompt
* Fixed recovering a background agent whose working directory was deleted showing a truncated stack trace instead of a clear error message
* Fixed `EnterWorktree` not being available immediately in background sessions (previously required `ToolSearch` first)
* Fixed `cmd+k` in iTerm2/Terminal.app not repainting attached background sessions
* Fixed the IME candidate window appearing at the bottom of the screen instead of next to the input caret in attached background sessions on Windows
* Fixed background-color bleed when attaching to a background agent from 256-color-only terminals after the agent had rendered file diffs
* Fixed `/copy` and copy-on-select silently failing to update the system clipboard when attached to a background session inside tmux
* Fixed opening `claude agents` with Remote Control enabled leaving zombie session entries on the Code tab after exiting
* Fixed `/rename` in background sessions not updating the session banner immediately
* Fixed Windows update rollback: if a Windows update fails, Claude Code now restores the original executable by copy and tells you how to recover
* \[VSCode] Fixed Claude Code processes not shutting down cleanly when VS Code closed on Windows, causing false "unclean exit" reports and orphaned MCP servers
* `/model` now saves your selection as the default for new sessions (matching the IDE). Press `s` in the picker to switch models for the current session only.
* If you customized the `modelPicker:setAsDefault` keybinding, rename it to `modelPicker:thisSessionOnly` in keybindings.json (the `d` action was replaced by `s`)

### 2.1.152 (May 27, 2026)

* `/code-review --fix` now applies review findings to your working tree after the review, surfacing reuse, simplification, and efficiency suggestions; `/simplify` now invokes `/code-review --fix`
* Skills and slash commands can now set `disallowed-tools` in frontmatter to remove tools from the model while the skill is active
* Added `/reload-skills` command to re-scan skill directories without restarting the session
* `SessionStart` hooks can now return `reloadSkills: true` to re-scan skill directories, making skills installed by the hook available in the same session
* `SessionStart` hooks can now set the session title via `hookSpecificOutput.sessionTitle` on startup and resume
* Added a `MessageDisplay` hook event that lets hooks transform or hide assistant message text as it is displayed
* Added `pluginSuggestionMarketplaces` managed setting: admins can allowlist org marketplaces whose plugins may be suggested via context-aware tips
* `claude plugin marketplace remove` now accepts `--scope user|project|local` for symmetry with `marketplace add`, `install`, and `uninstall`
* Claude Code now switches to your configured `--fallback-model` for the rest of the session when the primary model is not found, instead of failing every request
* Auto mode no longer requires opt-in consent
* Vim mode: `/` in NORMAL mode now opens reverse history search (like Ctrl+R), matching bash/zsh vi-mode
* The `/usage` breakdown now includes large session files; files are scanned with a streaming read so memory usage stays flat
* Thinking summaries in the collapsed group now stay readable for at least 3 seconds, render as markdown, and cap at 10 lines (`Ctrl+O` shows the full thinking)
* In fullscreen mode, the "Thinking for Ns" indicator now counts up live while the model is thinking, and keeps its value if you interrupt mid-thought
* Simplified the Workflow tool's inline progress display — live agent counts now show only in the persistent workflow status row below the prompt
* The post-response timer now shows "Waiting for N background agents/workflows to finish" when backgrounded agents or workflows are still running, and reports the cumulative time once their results are processed
* Added the session entrypoint as an OpenTelemetry metric attribute (`app.entrypoint`, opt-in via `OTEL_METRICS_INCLUDE_ENTRYPOINT=true`)
* Fixed terminal styling degrading in very long sessions by recycling the renderer's style pool
* Fixed the sandbox-enabled warning not appearing in condensed startup mode — it now shows in every layout
* Fixed the loading spinner showing "still thinking"/"almost done thinking" while a tool is running, and reset the thinking status to "thinking" after each tool
* Fixed focus mode showing a spurious "N messages hidden" count on turns with no hidden activity
* Fixed clicking a link inside an expanded tool result collapsing the section instead of opening the link
* Fixed markdown table cell borders inheriting the color of inline code, wrapped continuation lines losing their style, and empty header cells showing a label in the narrow-terminal stacked layout
* Fixed plugin MCP servers with the same command but different environment variables being incorrectly deduplicated
* Fixed `/doctor` reporting "marketplace not found" or "plugin not found" for stale `enabledPlugins` entries referencing removed marketplaces or dropped plugins
* Fixed plugins that track a git branch silently no longer receiving updates after the plugin registry was rebuilt
* Fixed remote MCP servers failing to connect in Claude Code Remote sessions when the egress proxy is enabled
* Fixed the effort-change confirmation dialog appearing when the conversation has no messages or when switching between effort levels that resolve to the same underlying value
* Fixed the Agent tool description referencing an agent list that is never delivered when running with `--bare` or with attachments disabled
* Fixed a background worker crash in `claude agents` when accepting a stale permission prompt after a subagent was cancelled
* Fixed `cache_creation_input_tokens` reporting as 0 in transcript and result usage when the API reports cache writes only via the nested `cache_creation` breakdown
* Fixed the PushNotification tool incorrectly reporting "Mobile push not sent (Remote Control inactive)" in SDK-hosted sessions when Remote Control is enabled
* Fixed sessions getting stuck after a model or login switch left stale thinking-block signatures in history; now stripped proactively with a retry safety-net

### 2.1.150 (May 23, 2026)

* Internal infrastructure improvements (no user-facing changes)

### 2.1.149 (May 22, 2026)

* `/usage` now shows a per-category breakdown of what's driving your limits usage — skills, subagents, plugins, and per-MCP-server cost
* `/diff` detail view can now be scrolled with the keyboard (arrows, `j`/`k`, `PgUp`/`PgDn`, `Space`, `Home`/`End`)
* Markdown output now renders GFM task list checkboxes (`- [ ] todo` / `- [x] done`) instead of plain bullets
* Enterprise: added the `allowAllClaudeAiMcps` managed setting to load claude.ai cloud MCP connectors alongside `managed-mcp.json`
* Fixed a PowerShell permission bypass: built-in `cd` functions (`cd..`, `cd\`, `cd~`, `X:`) changed the working directory undetected, letting a later command read outside the workspace
* Fixed the sandbox write allowlist in git worktrees covering the entire main repository root instead of only the shared `.git` directory (with `hooks/` and `config` denied)
* Fixed PowerShell prefix/wildcard allow rules (e.g. `PowerShell(dotnet.exe build *)`) not pre-approving native executables and scripts
* Fixed a permission-analysis gap where the parser trusted stale variable-tracking values for `PWD`/`OLDPWD`/`DIRSTACK` across `cd`/`pushd`/`popd`
* Fixed `find` in the Bash tool exhausting the macOS system file/vnode table and crashing the host on large directory trees
* Fixed the managed-settings approval dialog leaving the terminal frozen after accepting at startup
* Fixed `/ultraplan` and remote session creation failing with "Could not capture uncommitted changes" when the working tree has no real changes
* Fixed `otelHeadersHelper` failing silently when the script path contains spaces; helper failures are now reported in `/doctor` and the debug log
* Fixed the thinking spinner staying amber across tool calls and onto fresh thinking bursts
* Fixed collapsed Bash output reporting the wrong hidden-line count for outputs with many short lines
* Fixed slash-command argument-hint clipping trailing typed characters when the hint overflows the input box
* Fixed argument-hint and progressive arg suggestions not appearing after Tab-completing a skill whose frontmatter `name:` differs from its directory basename
* Fixed the status bar showing the user's baseline `/effort` setting instead of the effort level applied by skill/agent `effort:` frontmatter
* Fixed Ctrl+O transcript view freezing at the moment it was opened instead of tailing new messages
* Fixed editing a recalled prompt-history entry losing the edit when navigating further up/down with arrow keys
* Fixed `/config` exit summary reporting phantom changes to auto-compact and theme when toggling unrelated settings
* Fixed `/insights` crashing when cached session-meta files are missing optional fields
* Fixed malformed PowerShell and History tool calls with missing input being misclassified as reads in transcript collapsing
* Fixed renaming a Remote Control session from claude.ai or the Claude mobile app not updating the local session name for `claude --resume`
* Fixed a race where a just-submitted prompt could appear twice in the up-arrow history
* Fixed tapping the "Jump to bottom" pill in fullscreen mode not dismissing it immediately
* Improved `/feedback` reports to include the conversation that happened before context compaction, making issues from earlier in long sessions easier to triage

### 2.1.148 (May 22, 2026)

* Fixed the Bash tool returning exit code 127 on every command for some users (a regression introduced in 2.1.147)

### 2.1.147 (May 21, 2026)

* Pinned background sessions (`Ctrl+T` in `claude agents`) now stay alive when idle, are restarted in place to apply Claude Code updates, and are shed under memory pressure only after non-pinned sessions
* Renamed `/simplify` to `/code-review`. It now reports correctness bugs at a chosen effort level (e.g., `/code-review high`); pass `--comment` to post findings as inline GitHub PR comments. The old cleanup-and-fix behavior has been removed
* Improved auto-updater: retries transient network failures, reports specific error categories and OS error codes on failure, and shows the current version when an update fails
* Improved diff rendering performance for large file edits
* Prompt history no longer records consecutive duplicate entries — recalling a prompt with arrow-up and submitting it again won't add another copy
* Fixed enterprise login restrictions (`forceLoginOrgUUID` and `forceLoginMethod` managed-settings) not being enforced against third-party-provider and API-key sessions
* Fixed `&` in `!` command output displaying as `&`, which broke copy-pasting URLs from commands like `gcloud auth login` on headless machines
* Fixed unknown slash commands silently doing nothing in headless/SDK mode — they now show an error message
* Fixed `/help` rendering a broken tab header and showing only one command per page on small terminals when not in fullscreen mode
* Fixed shell snapshot dropping user functions whose names start with a single underscore, which broke aliases referencing them
* Fixed plugin agents that declare multiple `Agent(...)` types in `tools:` frontmatter dropping all but the last entry
* Fixed hook `if` conditions like `PowerShell(git push*)` never matching — only `PowerShell(*)` worked
* Fixed PowerShell tool dropping output for commands that rely on the default formatter
* Fixed: on Windows, "Yes, and don't ask again" for a PowerShell script invocation now writes a rule that actually matches on subsequent runs
* Fixed PowerShell tool failing on Windows with exit code 1 when `pwsh` is installed via winget or the Microsoft Store
* Fixed `/effort` opening with the slider on the wrong level — it now starts at your current effort
* Fixed paginating MCP servers dropping resources, templates, and prompts past page 1
* Fixed full-screen strobing in attached background sessions on Windows Terminal while Claude is streaming
* Fixed: on Windows, removing a background-job worktree no longer follows NTFS junctions into the main repo
* Fixed `/background` refusing sessions whose only typed input was a skill or custom slash command
* Fixed auto mode suppressing `AskUserQuestion` when the user or a skill explicitly relies on it; the auto-mode classifier now sees the user's answers as intent signal
* Fixed `/theme` "New custom theme" and color editor dialogs not responding to Esc
* Fixed an uncaught exception at the end of streaming sessions when running via the Agent SDK
* Fixed a rare hang when waiting for scroll to settle on Windows
* Fixed stale and doubled rows in the agent view list on Windows when background session results contain wide (CJK) characters
* Fixed pasted text being delivered to agents as an unreadable `[Pasted text #N]` placeholder instead of the actual content
* Fixed plugin component counts in `claude plugin details` and `/plugin` being doubled when a plugin's manifest listed paths overlapping its default directories
* Fixed backgrounded sessions re-prompting for tool permissions you already granted with "don't ask again"
* Fixed GNOME Terminal right-click and middle-click paste not inserting text
* Fixed `CLAUDE_CODE_SUBAGENT_MODEL` not applying to teammate processes spawned by agent teams
* Fixed slash commands followed by a tab or newline being treated as an unknown command
* Fixed several spacing and layout glitches in the `/plugin`, `/status`, `/mobile`, `/sandbox`, and `/permissions` menus
* Fixed stripped images prompting the model to repeatedly re-read media that was no longer present

### 2.1.145 (May 19, 2026)

* Added `claude agents --json` to list live Claude sessions as JSON for scripting (tmux-resurrect, status bars, session pickers)
* Added `agent_id` and `parent_agent_id` attributes to `claude_code.tool` OTEL spans, and fixed trace parenting so background subagent spans nest under the dispatching Agent tool span
* Status line JSON input now includes GitHub repo and PR information when detected
* `/plugin` Discover and Browse screens now show a plugin's commands, agents, skills, hooks, and MCP/LSP servers before installation
* `claude agents` terminal tab title now shows the awaiting-input count so an alt-tabbed window tells you when an agent needs attention
* Slash command and @-mention suggestion list now supports mouse hover and click in fullscreen mode
* Stop and SubagentStop hook input now includes `background_tasks` and `session_crons` fields
* Fixed a permission-prompt bypass where bare variable assignments to non-allowlisted environment variables in Bash commands were auto-approved
* Fixed MCP prompt slash commands showing raw server validation errors when a required argument is omitted — the error now names the missing argument and shows expected usage
* Fixed the spinner and elapsed-time display freezing until a keypress after the terminal was resized or refocused
* Fixed the cross-project resume hint failing in default Windows PowerShell 5.1 — Windows now uses `;` as the command separator
* Fixed voice push-to-talk not working in the agent view's reply pane
* Fixed task lists rendering in random order when several tasks are created at once
* Fixed stale "Failed to install Anthropic marketplace" banner showing when the marketplace is already installed
* Fixed the PR badge in the footer not updating immediately after `gh pr create` and other PR-state-changing commands run in-session
* Fixed Agent Teams teammates with non-ASCII names failing every API call due to invalid header encoding
* Fixed `/review` using a deprecated `projectCards` GraphQL query that errored on repos with Classic Projects
* Fixed `claude plugin validate` not flagging `skills:` entries that point at a file instead of a directory — the error now suggests the parent directory
* Fixed an infinite loop where a skill using `context: fork` could repeatedly re-invoke itself instead of running
* Improved the Read tool to return a truncated first page with a "PARTIAL view" notice instead of a hard error when a whole-file read exceeds the token limit

### 2.1.144 (May 19, 2026)

* Added `/resume` support for background sessions — sessions started via `claude --bg` or agent view now appear alongside interactive ones, marked with `bg`
* Added elapsed duration to background subagent completion notifications (e.g. "Agent completed · 3h 2m 5s")
* The `/plugin` browse and discover panes now show when a plugin was last updated
* `/model` now changes the model for the current session only; press `d` in the model picker to set a default for new sessions
* Renamed "extra usage" to "usage credits" across CLI copy; `/extra-usage` is now `/usage-credits` (old name still works)
* Fixed startup hanging up to 75s when `api.anthropic.com` is unreachable (captive portal, firewall, VPN issues) — side-channel API calls now time out after 15s
* Fixed garbled terminal output after a missed window-resize event (e.g. dragging a VS Code split-pane divider) — now self-heals on the next frame instead of requiring Ctrl+L
* Fixed progressive terminal display corruption (stale/garbled glyphs) that could appear in very long sessions and only cleared on terminal resize or restart
* Reduced terminal rendering glitches in VS Code by reducing spinner animation color count
* Fixed macOS background sessions crashing with "exit 1 before init" when the project lives under a Full Disk Access-protected folder (regression in 2.1.143)
* Fixed an unrecoverable conversation when reading a file whose image extension doesn't match its contents (e.g. HTML saved as .png) — now falls back to text
* Fewer spurious tool errors during search: `head`/`tail` file views now satisfy the read-before-edit check, and a "no matches" result (exit code 1) from `egrep`, `fgrep`, `git grep`, or `git diff` is no longer reported as a command failure
* Fixed `/branch` failing with "No conversation to branch" after entering a worktree or in some background sessions
* Fixed pressing Escape in the AskUserQuestion notes field aborting the turn instead of returning to answer selection
* Fixed model selection not applying when changed via the IDE model picker or `applyFlagSettings` after startup
* Resumed sessions now keep the model they were using instead of picking up another session's `/model` choice
* Fixed Bedrock and Vertex users unable to select "Opus (1M context)" from the `/model` picker (regression in v2.1.129)
* Fixed remote-session login failing with "Can't access this organization" for users with `forceLoginMethod` and `forceLoginOrgUUID` set
* Fixed MCP servers with paginated `tools/list` responses only returning the first page, silently dropping tools
* Fixed MCP images with unsupported MIME types (e.g. SVG) breaking the conversation — now saved to disk and referenced in the tool result
* Fixed file descriptor exhaustion when a build runs inside a skill directory — non-`.md` files no longer trigger skill reloads
* Fixed session title being generated from plugin monitor output instead of the user's first prompt
* Fixed Skill tool failing with permission error in headless mode (regression in v2.1.141)
* Fixed plugins enabled in your own settings showing "not cached" errors after first load on a fresh machine; plugins enabled only by a project's `.claude/settings.json` now show an actionable `claude plugin install` hint
* Fixed `claude mcp list` silently reporting no servers when `.mcp.json` can't be parsed (e.g. using VS Code's `"servers"` key instead of `"mcpServers"`) — now shows configuration errors
* Fixed background side-queries on custom `ANTHROPIC_BASE_URL` setups and Bedrock Mantle not using Haiku — now falls back correctly when a first-party API key is configured or no Haiku model is set
* Fixed scrolling in attached background sessions on Windows — PgUp/PgDn, mouse wheel, and Ctrl+O transcript navigation now work
* Fixed a crash when closing the terminal while attached to a background session
* Fixed on Windows, pressing ← in `claude agents` leaving the list unresponsive to keyboard input
* Fixed ghost characters at the left edge when switching panes in Agent View on Windows Terminal with CJK content
* `/bg` and `←`-detach now preserve directories added via `/add-dir`
* Fixed Edit/Write refusing with "background session hasn't isolated its changes yet" right after detaching a session that was already editing in place
* Fixed `claude respawn <id>` on a stopped background session showing "stopped" instead of running
* Fixed `/resume` picker not showing sessions forked from a background session
* Fixed opening a session from `claude agents` or running `claude logs <id>` hanging when the background service is unresponsive — now times out after 10s with a recovery hint
* Fixed background Bash tasks spawned by subagents staying "Running" in SDK task panels after the process exits
* Fixed completed or stopped background sessions briefly failing to wake being permanently marked as a startup crash
* Fixed markdown links in `claude agents` attached sessions rendering as plain text instead of clickable hyperlinks
* Fixed custom `spinnerVerbs` applying to the post-turn duration message — past-tense built-ins like "Worked for 5s" are restored there
* `claude agents` / `--bg` rejection messages now name the specific gate (non-TTY, env var, or setting) instead of a generic message
* `claude --bg --name <label>` now echoes the name in the post-spawn confirmation
* `claude agents`: renaming a background session with Ctrl+R now updates the attached session's banner immediately
* Background session worktree isolation guard now applies for non-git VCS users with `WorktreeCreate` hooks configured
* Plugin marketplace add/update now respects `CLAUDE_CODE_PLUGIN_PREFER_HTTPS`
* `/plugin` now returns to the Installed list after enabling, disabling, or uninstalling a plugin
* `/doctor` now shows an exec-form example when a command hook is missing the `command` field
* Skill-listing truncation is no longer shown as a startup notification — run `/doctor` for the full breakdown
* Improved recovery from rare pre-response stream stalls — now retries streaming once instead of falling back to a slower non-streaming request
* Improved SDK/headless MCP startup: pre-wait now overlaps startup instead of blocking before the first turn (up to 2s faster with slow MCP servers)
* The post-survey follow-up hint now appears after every non-dismiss survey response with context-aware copy, making it easier to share more detail via /feedback.

### 2.1.143 (May 15, 2026)

* Added plugin dependency enforcement: `claude plugin disable` now refuses when another enabled plugin depends on the target (with a copy-pasteable disable-chain hint), and `claude plugin enable` force-enables transitive dependencies
* Added projected context cost (per-turn and per-invocation token estimates) to the `/plugin` marketplace browse pane
* Added `worktree.bgIsolation: "none"` setting to let background sessions edit the working copy directly without `EnterWorktree`, for repos where worktrees are impractical
* PowerShell tool now passes `-ExecutionPolicy Bypass`. Opt out with `CLAUDE_CODE_POWERSHELL_RESPECT_EXECUTION_POLICY=1`
* Background sessions now preserve the model and effort level you set after waking from idle
* Shift+Tab in attached agent sessions now includes auto mode in the cycle
* Fixed a corrupt `.credentials.json` with a non-array `scopes` value hanging the CLI on startup or silently aborting OAuth token refresh
* Fixed right-click paste in `claude agents` on Windows Terminal and WSL
* Fixed stop hooks that block repeatedly looping forever — the turn now ends with a warning after 8 consecutive blocks (override via `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`)
* Fixed Esc/Ctrl+C not cancelling a pending `/loop` wakeup while Claude is idle between iterations
* Fixed `/goal` evaluator firing while background shells or delegated subagents are still running
* Fixed `NO_COLOR`/`FORCE_COLOR` in settings.json `env` stripping Claude Code's own UI colors — they now apply to subprocesses only
* Fixed agent view spawning repeated PowerShell processes on Windows when listing sessions
* Fixed `/bg` without a prompt sending "continue" to the forked session — the fork now waits for input
* Fixed `--agent <name>` not finding plugin-contributed agents without the `plugin:` prefix
* Fixed deleting a session from agent view not removing its transcript file
* Fixed stale-fragment rendering when scrolling in attached background sessions on Windows Terminal
* Fixed background agents false-positive worker-stall detection storm after host sleep or macOS App Nap
* Fixed 5xx error messages pointing at status.claude.com instead of naming the configured gateway or cloud provider
* The PowerShell tool is now enabled by default on Windows for Bedrock, Vertex, and Foundry users. Opt out with `CLAUDE_CODE_USE_POWERSHELL_TOOL=0`.
* `claude agents` now accepts `--add-dir`, `--settings`, `--mcp-config`, and `--plugin-dir` and applies them to the dashboard and to background sessions dispatched from it
* `claude agents` accepts `--permission-mode`, `--model`, `--effort`, and `--dangerously-skip-permissions` to set defaults for sessions dispatched from the view
* `claude --bg --dangerously-skip-permissions` now persists across retire→wake
* Fixed background sessions silently capturing IDE file references into the warm spare's input, which caused the reference to be prepended to the next prompt dispatched from `claude agents`
* Worktree cleanup no longer falls back to `rm -rf` when `git worktree remove` fails, preventing loss of gitignored or in-progress files
* Fixed background-job sessions on macOS getting "Operation not permitted" errors when reading files under `~/Documents`, `~/Desktop`, or `~/Downloads`, even with Full Disk Access granted.
* `/bg` now preserves `--mcp-config`, `--settings`, `--add-dir`, `--plugin-dir`, and `--strict-mcp-config`, so backgrounded sessions keep their MCP servers and settings across respawn.
* Background sessions launched from `claude agents` now honor `permissions.defaultMode` from settings.json (was previously overridden to auto mode)
* Fixed: on Windows, pressing ← in `claude agents` while a response was streaming could leave the agents list unresponsive to all input
* `/bg` and `←`-detach now preserve `--fallback-model`, so backgrounded workers degrade to the fallback model on overload instead of hard-failing.
* `/bg` and `←`-detach now preserve `--allow-dangerously-skip-permissions`, so the forked worker keeps bypass-permissions available in its Shift+Tab cycle.
* Fixed: background daemon spawn now falls back to the running binary when the `~/.local/bin/claude` launcher is missing or non-executable
* Fixed `claude agents --allow-dangerously-skip-permissions` defaulting dispatched sessions to bypass mode instead of making it available in the permission cycle

### 2.1.142 (May 14, 2026)

* Added new `claude agents` flags: `--add-dir`, `--settings`, `--mcp-config`, `--plugin-dir`, `--permission-mode`, `--model`, `--effort`, and `--dangerously-skip-permissions` to configure dispatched background sessions
* Fast mode now uses Opus 4.7 by default (previously Opus 4.6). Set `CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE=1` to pin fast mode to Opus 4.6
* Plugins with a root-level `SKILL.md` and no `skills/` subdirectory are now surfaced as a skill
* The `/plugin` details pane and `claude plugin details` now show LSP servers a plugin provides
* `/web-setup` warns before replacing an existing GitHub App connection
* Fixed `MCP_TOOL_TIMEOUT` not raising the per-request fetch timeout for remote HTTP and SSE MCP servers, which capped tool calls at 60 seconds regardless of the configured value
* Fixed background sessions not recognizing pre-existing git worktrees, blocking Edit while EnterWorktree refused to create a duplicate
* Fixed background sessions disappearing and daemon reconnect failing after macOS sleep/wake — the daemon now detects clock jumps instead of treating them as elapsed idle time
* Fixed daemon not exiting cleanly after the binary is upgraded (e.g. `brew upgrade`), causing dispatched agents to crash-loop on the deleted path
* Fixed background agents crash-looping when the Claude-in-Chrome extension is connected without a shared tab
* Fixed clicking links in an attached `claude agents` session — the background worker's headless browser shim no longer applies while attached
* Fixed `claude agents` "v to open in editor" using the daemon's default editor instead of your shell's `$EDITOR`/`$VISUAL`
* Fixed `claude agents` deadlocking on Windows with network-drive working directories; Ctrl+C now works during startup
* Fixed background-color bleed when attaching to a `claude agents` session from Apple Terminal or other 256-color-only terminals
* Fixed `claude --bg --dangerously-skip-permissions` not persisting across retire/wake
* Fixed session titles being derived from the URL when the first message is a link
* Fixed redundant `set_model` requests from remote clients injecting duplicate `/model` breadcrumbs into the transcript
* Fixed plugins using `skills: ["./"]` showing a false "path escapes plugin directory" error
* Fixed plugin cache cleanup deleting the active plugin version directory when no installation metadata is present
* Fixed `/plugin` browse pane showing "0 installs" for newly published plugins
* Fixed plugin advisories not naming every `plugin.json` key that shadows a default folder
* Improved reactive compaction: the first summarize attempt now seeds from the original request's overflow size, avoiding a wasted near-full-context retry
* Improved hook configuration error: configuring a prompt- or agent-type hook for `SessionStart`/`Setup`/`SubagentStart` now shows a clear "use a command-type hook instead" error
* Removed stale `/model claude-sonnet-4-20250514` suggestion from Usage Policy refusal messages

### 2.1.141 (May 13, 2026)

* Added `terminalSequence` field to hook JSON output so hooks can emit desktop notifications, window titles, and bells without a controlling terminal
* Added `CLAUDE_CODE_PLUGIN_PREFER_HTTPS` to clone GitHub plugin sources over HTTPS instead of SSH, for environments without a GitHub SSH key
* Added `ANTHROPIC_WORKSPACE_ID` environment variable for workload identity federation — scopes the minted token to a specific workspace when the federation rule covers more than one
* Added `claude agents --cwd <path>` to scope the session list to a directory
* `/feedback` can now include recent sessions (last 24 hours or 7 days) for issues spanning more than the current session
* Rewind menu: added "Summarize up to here" to compress earlier context while keeping recent turns intact
* Auto mode permission dialog now explains when a `permissions.ask` rule caused the prompt
* Restored the "view diff in your IDE" option on file-edit permission prompts when an IDE is connected
* Background agents launched via `/bg` or `←←` now preserve the current permission mode instead of reverting to default
* `claude agents`: agents that finish work but leave a background shell running now move to Completed instead of staying under Working
* Improved spinner feedback during long thinking periods — the spinner now warms to amber after 10 seconds to signal Claude is still working
* Improved plugin menu navigation: `→`/Tab switch tabs, `↑` moves to the tab strip, and tab headers and search box are clickable in fullscreen mode
* Fixed background side-queries sending an unavailable Haiku model ID on Bedrock/Vertex/Foundry/gateway when no `ANTHROPIC_SMALL_FAST_MODEL` override is set — now falls back to the main-loop model
* Fixed `claude daemon status` and `/doctor` on Windows throwing when the daemon pipe key file is locked or unreadable — now shows the underlying error instead of an opaque failure
* Fixed `claude agents` showing the agent-type list instead of the dashboard when launched through a wrapper that adds flags
* Fixed `claude agents` opening a crashed session firing redundant dispatches when the working directory was deleted
* Fixed background jobs on a custom `ANTHROPIC_BASE_URL` gateway not getting auto-named — the namer now uses the main model when no Haiku model is configured
* Fixed `/model` in one session silently changing the autocompact threshold in other concurrent sessions
* Fixed switching permission mode while a tool-permission prompt is open not auto-dismissing the prompt when the new setting permits the tool
* Fixed pressing Enter while a permission/dialog prompt is open also submitting text in the input box
* Fixed hooks receiving a non-existent `transcript_path` after `EnterWorktree` switches the working directory
* Fixed markdown tables with cell wrapping falling back to the vertical key-value layout instead of rendering as a bordered grid (regression in 2.1.136)
* Fixed cancelled prompts being removed from Up-arrow history when auto-restored into the input box, avoiding duplicate entries
* Fixed prompts cancelled with Ctrl+C/Esc before any response being dropped from Up-arrow history
* Fixed Ctrl+C not interrupting a running turn while in vim INSERT/VISUAL mode
* Fixed alternative `chat:submit` keybindings (e.g. `meta+enter`, `ctrl+enter`) not working when `enter` is rebound to `chat:newline`
* Fixed prompt suggestions being silently disabled when an output style was configured
* Fixed `spinnerVerbs` setting not being honored in turn-completion messages
* Fixed AskUserQuestion popup hiding the last line of preceding chat content
* Fixed Web Search status showing "Did 0 searches" when searches returned errors
* Fixed multi-line statusline output dropping or corrupting rows when any line exceeds terminal width
* Fixed light-ansi theme using invisible white for diff context lines on light backgrounds — now uses black
* Fixed error overlay dumping minified bundle source that hid the original error message
* Fixed pressing Enter after typing a feedback survey rating digit submitting it as a chat message instead of the rating
* Fixed pressing `x` on a selected subagent in the agent panel typing into the prompt instead of stopping the agent
* Fixed session title being derived from plugin monitor notifications before the user's first prompt
* Fixed "Allowed by PermissionRequest hook" repeating once per tool call under a collapsed read/search group
* Fixed `/tui` silently dropping running background shells and subagents — now refuses and asks to wait for them to finish
* Fixed welcome banner showing "API Usage Billing" on Bedrock, Vertex, Foundry, and other third-party providers — now shows the provider name
* Fixed `/mcp` server list not keeping the focused server visible in short terminals in fullscreen mode
* Fixed redaction in `/feedback` bundles producing invalid JSON for quoted values like session IDs
* Fixed desktop and third-party provider sessions incorrectly inheriting `apiKeyHelper`/`ANTHROPIC_AUTH_TOKEN` from host managed-settings
* Fixed early analytics events being silently dropped when fired before logger initialization
* Fixed `claude plugin install` failing for plugins whose marketplace `ref` no longer exists upstream when a `sha` is also pinned
* Fixed plugin details pane showing 0 MCP servers for plugins that declare them via `.mcp.json`
* Fixed plugin MCP servers with unset config variables showing a generic connection failure instead of a "config issue" message with a fix-it hint; malformed `.mcp.json` entries no longer drop other MCP servers
* Fixed MCP server configs using POSIX shell parameter expansions (e.g. `${var%pattern}`) being incorrectly flagged as missing environment variables
* Fixed MCP HTTP/SSE servers returning 403 on connect showing as "failed" instead of "needs auth"
* Fixed remote MCP servers disconnecting unnecessarily when the optional server-events stream failed to reconnect — tool calls continue over POST
* Fixed Remote Control MCP connectors all failing with 401 when the worker session token rotated mid-session
* Fixed Remote Control automatically re-enrolling a trusted device when the server rejects a stale token, instead of looping through `/login`
* Fixed a race where early OTel spans could be silently dropped in SDK/headless mode with beta tracing enabled
* Fixed custom `voice:pushToTalk` keybindings and `"space": null` unbinds being silently ignored
* Fixed Windows Alt+V image paste reporting "no image found" when the clipboard contains a screenshot
* Fixed SDK "Claude Code native binary not found" on Linux when both glibc and musl platform packages are installed
* Bedrock: `awsCredentialExport` now always runs when configured instead of being skipped when ambient AWS credentials resolve, fixing auth for cross-account access
* \[VSCode] Fixed in-chat mic showing no feedback when the microphone produced only silence — now shows "No audio detected"
* \[VSCode] Voice mode: the WSL error now suggests installing `sox libsox-fmt-pulse` for WSLg users
* `claude agents`: launching a session no longer fails when the pre-warmed background worker is unhealthy — now falls back to a fresh launch
* `claude agents` no longer shows empty placeholder sessions left over from backgrounding a fresh REPL, and shows onboarding text when entered via ← with no other agents
* Empty idle background sessions left over from `←` are now automatically retired by the daemon after 5 minutes

### 2.1.140 (May 12, 2026)

* Improved Agent tool `subagent_type` matching to accept case- and separator-insensitive values (e.g. `"Code Reviewer"` resolves to `code-reviewer`)
* Updated agent color palette
* Fixed `/goal` silently hanging when `disableAllHooks` or `allowManagedHooksOnly` is set — now shows a clear message instead of an indicator that never resolves
* Fixed a regression in settings hot-reload where symlinked settings files caused misattributed change events and spurious `ConfigChange` hooks
* Fixed `claude --bg` failing with "connection dropped mid-request" when the background service was about to idle-exit
* Fixed background service startup failing on machines with enterprise endpoint security by allowing more time
* Fixed remote managed settings not retrying on 401 — now retries once with a force-refreshed token
* Fixed managed `extraKnownMarketplaces` auto-update policy not being persisted to `known_marketplaces.json`
* Fixed `/loop` scheduling redundant wakeups to poll for background tasks that already notify on completion
* Fixed a recurring event-loop stall on Windows when a missing executable (e.g. `gh`) triggered synchronous `where.exe` re-spawns on every check
* Fixed `Read` tool calls failing validation when `offset` is passed as a whitespace-padded or `+`-prefixed string
* Fixed native terminal cursor not staying at the input caret when the terminal loses focus
* Plugins now warn when a default component folder (e.g. `commands/`) is silently ignored because `plugin.json` sets the matching key. Shown in `/doctor`, `claude plugin list`, and `/plugin`.

### 2.1.139 (May 11, 2026)

* Added agent view (Research Preview): a single list of every Claude Code session — running, blocked on you, or done. Run `claude agents` to get started. See [https://code.claude.com/docs/en/agent-view](https://code.claude.com/docs/en/agent-view)
* Added `/goal` command: set a completion condition and Claude keeps working across turns until it's met. Works in interactive, `-p`, and Remote Control. Shows live elapsed/turns/tokens as an overlay panel
* Added `/scroll-speed` command to tune mouse wheel scroll speed with a live preview
* Added `claude plugin details <name>` to show a plugin's component inventory and projected per-session token cost
* Added transcript view navigation: `?` for keyboard shortcuts, ``/`` to jump between user prompts, `v` to toggle shortcut panel
* Added hook `args: string[]` field (exec form) that spawns the command directly without a shell, so path placeholders never need quoting
* Added hook `continueOnBlock` config option for `PostToolUse` — set to `true` to feed the hook's rejection reason back to Claude and continue the turn
* MCP stdio servers now receive `CLAUDE_PROJECT_DIR` in their environment, matching hooks. Plugin configs can reference `${CLAUDE_PROJECT_DIR}` in commands
* Compaction prompt now asks the model to preserve sensitive user instructions
* `/mcp` Reconnect now picks up `.mcp.json` edits without a restart, and shows the HTTP status and URL when reconnecting fails
* `/context all` per-skill token estimates now account for the model's tokenizer and show rounded values
* `claude plugin install <name>@<marketplace>` now auto-refreshes the marketplace and retries before reporting a plugin as not found
* `/plugin` installed-plugin details now show hook event names and MCP server names cleanly
* `/context` now shows the providing plugin's name for plugin-sourced skills
* Remote MCP server reconnect retry on transient failures is now enabled for all users
* API requests from subagents now carry `x-claude-code-agent-id` / `x-claude-code-parent-agent-id` headers, and `claude_code.llm_request` OTEL spans include `agent_id` / `parent_agent_id` attributes
* Remote Control, `/schedule`, claude.ai MCP connectors, and notification preferences are now disabled when `ANTHROPIC_API_KEY` / `apiKeyHelper` / `ANTHROPIC_AUTH_TOKEN` is set, even if a Claude.ai login also exists. Unset the API key to use these features
* Fixed a deadlock where expired credentials and the `forceRemoteSettingsRefresh` policy setting blocked `claude auth login`/`logout`/`status` with no way to recover
* Fixed `autoAllowBashIfSandboxed` not auto-approving commands with shell expansions like `$VAR` and `$(cmd)`
* Fixed a bug where a hook writing to the terminal could corrupt an on-screen interactive prompt; hooks now run without terminal access
* Fixed unbounded memory growth when an HTTP/SSE MCP server streams non-protocol data — response bodies now capped at 16 MB per SSE frame
* Fixed `Skill(name *)` permission rules — the wildcard form now works as a prefix match, matching `Bash(ls *)` behavior
* Fixed settings hot-reload not detecting edits to symlinked `~/.claude/settings.json`
* Fixed plugin details failing to load when the marketplace key differs from the manifest name
* Fixed `/model` picker "Default" row not reflecting `ANTHROPIC_DEFAULT_OPUS_MODEL`/`ANTHROPIC_DEFAULT_SONNET_MODEL` overrides
* Fixed spurious "stream idle timeout" 5 minutes after a response completed, caused by the watchdog timer not being cleared on stream cancellation
* Fixed silent `exit 1` when 10+ MCP servers are configured and the cache directory is unwritable — the error message now includes the underlying cause
* Fixed a typing cursor blinking on tab names, list pointers, and select rows in dialogs
* Fixed transcript view letter shortcuts not working after mouse click
* Fixed Bash-mode up-arrow history repeating the first entry and clobbering the in-progress draft
* Fixed pasting or dropping multiple images only inserting the last one
* Fixed hyperlinks using unreadable dark navy on dark themes — they now adapt to the active theme
* Fixed model picker showing a redundant "Current model" row for third-party users whose model is set to the `opus` alias
* Fixed legacy Opus picker entry on PAYG 3P providers resolving to the same model as the default entry
* Fixed mouse wheel scrolling speed in Cursor and VS Code 1.92–1.104; the trackpad now scrolls at a steady rate and the mouse wheel keeps \~3 lines per notch
* Fixed scroll behavior in Windows Terminal and VS Code when attached to background sessions
* Fixed MCP resources from disconnected servers lingering in `@server:` autocomplete
* Fixed two-file diff snippets over-reporting the number of truncated lines by one
* Fixed Grep results not relativizing Windows drive-letter paths and count mode reporting wrong totals for single-file paths
* Fixed border-embedded text overflowing on CJK/emoji due to visual cell width miscalculation
* Fixed fuzzy-match highlighting splitting emoji and astral-plane characters mid-pair
* Fixed skill argument names containing regex metacharacters breaking argument substitution
* Fixed ProgressBar rendering a full block for an almost-full fractional cell
* Fixed task polling and `fs.watch` being resurrected when the last subscriber leaves while a fetch is in flight
* Fixed plugin dependency resolution leaving a stale count when the manifest name differs from the source identifier
* Fixed Insights Time-of-Day chart skewing when a session has an unparseable timestamp
* Fixed keybindings using only the cmd/super/win modifier being flagged as unparseable
* Fixed `claude_code.active_time.total` OpenTelemetry metric not being emitted in `--print` mode
* Fixed `claude plugin update` not preserving cross-plugin symlinks inside a marketplace
* \[VSCode] Press Cmd/Ctrl+Shift+T to reopen the most recently closed session tab, configurable via `claudeCode.enableReopenClosedSessionShortcut`

### 2.1.138 (May 9, 2026)

* Internal fixes

### 2.1.137 (May 9, 2026)

* \[VSCode] Fixed extension failing to activate on Windows

### 2.1.136 (May 8, 2026)

* Added `CLAUDE_CODE_ENABLE_FEEDBACK_SURVEY_FOR_OTEL` to re-enable the session quality survey for enterprises capturing responses through OpenTelemetry
* Added `settings.autoMode.hard_deny` for auto mode classifier rules that block unconditionally regardless of user intent or allow exceptions
* Fixed MCP servers configured in `.mcp.json`, plugins, and claude.ai connectors silently disappearing after `/clear` in the VS Code extension, JetBrains plugin, and Agent SDK
* Fixed a rare login loop where a concurrent credential write could overwrite a freshly-rotated OAuth token and force re-login
* Fixed MCP OAuth refresh tokens being lost when multiple servers refresh concurrently — users with several remote MCP servers should no longer need daily re-authentication
* Fixed an API error (400) when extended thinking emitted a redacted thinking block after a tool call
* Fixed `--resume` / `--continue` not finding sessions when the project path contains underscores
* Fixed plan mode not blocking file writes when a matching `Edit(...)` allow rule exists
* WSL2: image paste from Windows clipboard now works via a PowerShell fallback when xclip/wl-paste cannot read image data
* Fixed plugin `Stop`/`UserPromptSubmit` hooks failing when cache cleanup deletes a version still in use by a running session
* Improved visual consistency across slash command dialogs: standardized footer hints, dialog spacing, and arrow-key styling, and the dialog frame now appears immediately during loading instead of popping in after
* Fixed colors appearing at wrong positions in bash command output and markdown code blocks
* Fixed ReasonML diffs rendering corrupted "undefined" text artifacts at word-diff boundaries
* Fixed worktree exit dialog warning about uncommitted files in the wrong directory after worktree removal
* Fixed `@` file picker not matching files created mid-session in small non-git directories
* Fixed `@`-mention file picker not finding files in directories with more than 100 entries
* Fixed failed tool calls not being click-to-expand in fullscreen mode when their output was truncated
* Fixed Backspace and Ctrl+Backspace getting swapped after using Ctrl+G to open an external editor on terminals with persistent extended-key modes
* Fixed `/usage` weekly reset showing time of day instead of the calendar date
* Fixed welcome banner ellipsis causing column overflow on CJK terminals
* Fixed `/insights` crash when session history contains tool calls with malformed input fields
* Fixed a renderer crash when a tool's collapsibility classification changes mid-session
* Fixed a `skills` entry in `plugin.json` hiding the plugin's default `skills/` directory, and listing a file path now shows an error instead of failing silently
* Fixed IDE shell-integration lock files not respecting `CLAUDE_CONFIG_DIR`
* Fixed trailing whitespace in copied terminal output during streaming
* Fixed plugin uninstall and enable/disable not matching slugs case-insensitively
* Fixed tool error truncation marker showing a negative count for surrogate-pair strings
* Fixed env vars from `CLAUDE_ENV_FILE` SessionStart hooks going stale after `/resume` or `/clear`
* Fixed `/branch` saving a multi-line session title when given a pasted multi-line name
* Fixed a stray leading space on the second line of wrapped text at the column boundary
* Fixed Esc not dismissing dialogs in `/install-github-app`, `/desktop`, `/resume`, and `/web-setup`
* Fixed `/doctor` MCP schema errors not naming the missing field or showing the source file path
* Fixed Bash permission prompts showing an internal parser diagnostic instead of a user-readable explanation
* Fixed plugin slash commands with spaces (e.g. `/myplugin review`) not resolving to their namespaced form
* Fixed `AskUserQuestion` discarding multi-select answers when supplied as an array
* Fixed `/clear <name>` not labeling the cleared session for `/resume`
* Fixed `CronList` output missing qualifiers and the scheduled prompt
* Fixed "Jump to bottom" overlay leaving color artifacts on CJK characters in fullscreen mode
* Fixed wide markdown tables leaving a stale bordered render in terminal scrollback while streaming
* Fixed pasted text being silently dropped when a long prompt with a pasted-text placeholder was auto-truncated
* Fixed `/release-notes` getting stuck on an old version after a failed changelog refresh
* Fixed `/mcp` server list not scrolling when there are more servers than fit in the terminal
* Fixed mid-input slash command autocomplete not working after an initial slash command
* Fixed scrolling to bottom re-engaging auto-follow with `autoScrollEnabled: false`
* Fixed prompt suggestions being auto-submitted by Enter on an empty input instead of requiring Tab or arrow to accept
* Fixed keyboard shortcut hints not reflecting rebound keys from `keybindings.json`
* Fixed `/settings` language change being reverted on Escape after confirming
* Fixed `/terminal-setup` only appearing in autocomplete on exact name match instead of partial prefixes
* Fixed "Chat about this" on an `AskUserQuestion` dialog erasing the question text
* Fixed MCP tool results being invisible when the server returns content blocks
* Improved error message when `--worktree` collides with an existing or stale worktree
* Changed plugin marketplace removal key to `d` (matching delete elsewhere) instead of `r` which collided with retry

### 2.1.133 (May 7, 2026)

* Added `worktree.baseRef` setting (`fresh` | `head`) to choose whether `--worktree`, `EnterWorktree`, and agent-isolation worktrees branch from `origin/<default>` or local `HEAD`. **Note:** the default `fresh` changes `EnterWorktree`'s base back to `origin/<default>` (it has been local `HEAD` since 2.1.128) — set `worktree.baseRef: "head"` to keep unpushed commits in new worktrees
* Added `sandbox.bwrapPath` and `sandbox.socatPath` managed settings (Linux/WSL) to specify custom bubblewrap and socat binary locations
* Added `parentSettingsBehavior` admin-tier key (`'first-wins' | 'merge'`) to let admins opt SDK `managedSettings` (parent tier) into the policy merge
* Hooks now receive the active effort level via the `effort.level` JSON input field and the `$CLAUDE_EFFORT` environment variable, and Bash tool commands can read `$CLAUDE_EFFORT`
* Improved focus mode behavior
* Improved memory usage by releasing warm-spare background workers under memory pressure
* Fixed parallel sessions all dead-ending at 401 after a refresh-token race wiped shared credentials
* Fixed `Edit`/`Write` allow rules scoped to a drive root (`C:\`) or POSIX `/` matching incorrectly and always prompting
* Fixed an unhandled rejection (`ECOMPROMISED`) when a history or session-log file lock is compromised by clock skew or slow disk
* Fixed pressing Esc during conversation compaction showing a spurious "Error compacting conversation" notification
* Fixed `HTTP(S)_PROXY` / `NO_PROXY` / mTLS not being respected for the full MCP OAuth flow including discovery, dynamic client registration, token exchange, and token refresh
* Fixed Read/Write/Edit being denied on mapped network drives passed via `--add-dir` / SDK `additionalDirectories`
* Fixed Remote Control stop/interrupt from claude.ai not fully canceling the CLI session the same way local Esc does, causing queued messages to never advance after interrupting a stuck tool or prompt
* Fixed `/effort` in one session unexpectedly changing the effort level of other concurrent sessions, and a related issue where an IDE effort change could be silently dropped
* Fixed subagents not discovering project, user, or plugin skills via the Skill tool
* `claude --help` now lists `--remote-control` alongside `--remote-control-session-name-prefix`
* \[VSCode] Fixed `claudeCode.claudeProcessWrapper` failing with "Unsupported platform" when the extension build doesn't bundle a Claude binary

### 2.1.132 (May 6, 2026)

* Added `CLAUDE_CODE_SESSION_ID` environment variable to the Bash tool subprocess environment, matching the `session_id` passed to hooks
* Added `CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN=1` env var to opt out of the fullscreen alternate-screen renderer and keep the conversation in the terminal's native scrollback
* Added a "Pasting…" footer hint while a Ctrl+V image paste is being read from the clipboard
* Fixed external SIGINT (e.g. IDE stop button, `kill -INT`) not running graceful shutdown — terminal modes are now restored and the `--resume` hint is printed instead of an abrupt exit
* Fixed an uncaught exception when the terminal is closed or SSH disconnects mid-session under the native build
* Fixed `--resume` failing with `no low surrogate in string` when a tool error truncation split an emoji; pre-corrupted sessions are sanitized on load
* Fixed `--permission-mode` flag being ignored when resuming a plan-mode session with `-p --continue`/`--resume`, and plan mode not being re-applied after `ExitPlanMode` within the same session
* Fixed fullscreen mode showing a blank screen after laptop sleep/wake or Ctrl+Z/`fg` until the next keystroke or stream output
* Fixed cursor landing mid-grapheme on Ctrl+E/A/K/U/arrow keys when an Indic conjunct or ZWJ emoji wraps across lines
* Fixed vim operators corrupting text containing decomposed (NFD) accented characters
* Fixed pasting text starting with `/` silently swallowing the input or triggering an unknown-command reply
* Fixed pasting dumping stray escape sequences into the prompt when focus events or mouse-tracking reports interleave with the bracketed paste
* Fixed mouse wheel scrolling being too fast in Cursor and VS Code 1.92–1.104 due to an upstream xterm.js bug
* Fixed scroll-wheel handling in JetBrains IDE 2025.2 terminals (spurious arrow keys, wrong-direction events, runaway acceleration)
* Fixed `/usage` Ctrl+S hanging when copying the stats screenshot to the clipboard on Linux/X11
* Fixed `/terminal-setup` showing a contradictory error in Windows Terminal — Shift+Enter is natively supported there
* Fixed `/effort` picker not reflecting the `CLAUDE_CODE_EFFORT_LEVEL` env var override
* Fixed `/status` showing the wrong default model for some users
* Fixed slash command autocomplete popup being capped at \~3–5 visible commands instead of scaling with terminal height
* Fixed statusline `context_window` token counts reflecting cumulative session totals instead of current context usage
* Fixed Alt+T (thinking toggle) not working on macOS terminals without "Option as Meta" enabled (iTerm2, Terminal.app defaults)
* Fixed dead keyboard input on Windows after re-opening a background session from `claude agents`
* Fixed unbounded memory growth (10GB+ RSS) when a stdio MCP server writes non-protocol data to stdout
* Fixed MCP servers that connect but fail `tools/list` silently showing 0 tools — they now retry once and show "connected · tools fetch failed" in `/mcp`
* Fixed unauthorized claude.ai MCP connectors showing as "failed" instead of "needs auth", and headless `-p` mode retrying non-transient 4xx connection failures
* Improved visual consistency in slash command dialogs and `/login`, `/upgrade`, `/extra-usage` dialog spacing
* Updated the `/tui fullscreen` startup banner to describe additional renderer benefits (lower memory usage, mouse support, auto-copy on select)
* Fixed Bedrock and Vertex 400 errors when `ENABLE_PROMPT_CACHING_1H` is set

### 2.1.131 (May 6, 2026)

* Fixed VS Code extension failing to activate on Windows due to a hardcoded build path in the bundled SDK (`createRequire` polyfill bug)
* Fixed Mantle endpoint authentication failing with missing `x-api-key` header

### 2.1.129 (May 6, 2026)

* Added `--plugin-url <url>` flag to fetch a plugin `.zip` archive from a URL for the current session
* Added `CLAUDE_CODE_FORCE_SYNC_OUTPUT=1` env var to force-enable synchronized output on terminals that auto-detection misses (e.g. Emacs `eat`)
* Added `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE`: when set on Homebrew or WinGet installations, Claude Code runs the upgrade command in the background and prompts to restart
* Plugin manifests: `themes` and `monitors` should now be declared under `"experimental": { ... }`. Top-level declarations still work but `claude plugin validate` will warn
* Gateway `/v1/models` discovery for the `/model` picker is now opt-in via `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1` (was automatic in 2.1.126–2.1.128)
* Ctrl+R history picker now defaults to searching all prompts across all projects, matching pre-2.1.124 behavior. Press Ctrl+S to narrow to the current project or session
* Third-party deployments (Bedrock, Vertex, Foundry, or `ANTHROPIC_BASE_URL` gateway) no longer see spinner tips pointing at first-party Anthropic surfaces
* `skillOverrides` setting now works: `off` hides from model and `/`, `user-invocable-only` hides from model only, `name-only` collapses description
* The `claude_code.pull_request.count` OTel metric now counts PRs/MRs created via MCP tools, not just shell commands
* Policy refusal error messages now include the API Request ID for easier support debugging
* Fixed API errors with unrecognized 400 status codes showing raw JSON instead of the underlying error message
* Fixed `/clear` not resetting the terminal tab title after a conversation
* Fixed session title chip from `/rename` disappearing while a permission or other dialog is active
* Fixed agent panel below the prompt being hidden when subagents are running (regression in 2.1.122)
* Fixed external-editor handoff (Ctrl+G) blanking the conversation history above the prompt
* Fixed `/context` dumping its rendered ASCII visualization grid into the conversation, wasting \~1.6k tokens per call
* Fixed `/agents` Library list arrow-key navigation: the highlighted agent now stays visible when the list exceeds the viewport
* Fixed `/branch` success message not including the new branch's session id for `/resume`
* Fixed bold headers with keycap/ZWJ/skin-tone emoji losing trailing characters in fullscreen mode
* Fixed server-managed settings policy not applying for enterprise/team users whose stored OAuth credentials lacked the `user:inference` scope
* Fixed OAuth refresh race after wake-from-sleep that could log out all running sessions
* Fixed 1-hour prompt cache TTL being silently downgraded to 5 minutes
* Fixed cache-miss warning appearing spuriously after `/clear` or compaction when changing `/effort` or `/model`
* Fixed `Bash(mkdir *)`, `Bash(touch *)` and similar allow rules not being honored for in-project paths
* Fixed `deniedMcpServers` patterns with a `*://` scheme wildcard not matching mixed-case hostnames
* Fixed harmless WebSocket warning being logged as an error in `--debug` during voice mode
* \[VSCode] Fixed `/clear` not clearing the conversation context and displayed transcript

### 2.1.128 (May 4, 2026)

* Bare `/color` (no args) now picks a random session color
* `/mcp` now shows the tool count for connected servers and flags servers that connected with 0 tools
* `--plugin-dir` now accepts `.zip` plugin archives in addition to directories
* `--channels` now works with console (API key) authentication — console orgs with managed settings must set `channelsEnabled: true` to enable
* Updated `/model` picker: collapsed duplicate Opus 4.7 entries, and current Opus now shows as "Opus" instead of "Opus 4.7"
* Subprocesses (Bash, hooks, MCP, LSP) no longer inherit `OTEL_*` environment variables, so OTEL-instrumented apps run via the Bash tool no longer pick up the CLI's own OTLP endpoint
* MCP: `workspace` is now a reserved server name — existing servers with that name will be skipped with a warning
* Reconnecting MCP servers no longer flood the conversation with full tool-name lists on every reconnect — re-announced tools are summarized by server prefix
* SDK hosts now receive a persistent `localSettings` suggestion for Bash permission prompts, so "Always allow" writes to `.claude/settings.local.json`
* `EnterWorktree` now creates the new branch from local HEAD as documented, instead of `origin/<default-branch>` — unpushed commits are no longer dropped
* Auto mode: when the classifier can't evaluate an action, the error now includes a hint (retry, `/compact`, or run with `--debug`)
* Fixed focus mode briefly dimming the previous response when submitting a new prompt
* Fixed stray "4;0;" desktop notification on every `/exit` in Kitty and other terminals that interpret OSC 9 as a notification
* Fixed Remote Control showing an empty "Opening your options…" message on rate limit instead of actionable upsell options
* Fixed drag-and-drop image upload hanging on "Pasting text…" when the image read fails
* Fixed crash loop when piping very large input (>10 MB) to `claude -p` via stdin
* Fixed long URLs not being individually clickable on every wrapped row in fullscreen mode
* Fixed `/plugin` Components panel showing "Marketplace 'inline' not found" for plugins loaded via `--plugin-dir`
* Fixed MCP tool results dropping images when the server returns both structured content and content blocks
* Fixed fenced code blocks inside list items carrying leading whitespace into the clipboard on copy-paste
* Fixed tab navigation in `/config` stranding focus — the tab header now stays focused so arrows and Esc keep working
* Fixed markdown link labels being lost on terminals without OSC 8 hyperlink support — links now render as `label (url)` instead of just the URL
* Fixed sessions on 1M-context models with a smaller autocompact window being falsely blocked with "Prompt is too long" before reaching the actual API limit
* Fixed parallel shell tool calls: a failing read-only command (grep, git diff, ls) no longer cancels sibling calls
* Fixed banner showing "with X effort" on models that don't support effort
* Fixed `/fast` on 3P providers fuzzy-matching to an unrelated skill instead of showing "not available"
* Fixed Bedrock default model resolving to `global.*` instead of the region-appropriate prefix
* Fixed vim mode: `Space` in NORMAL mode now moves the cursor right, matching standard vi/vim behavior
* Fixed terminal progress indicator (OSC 9;4) flickering off between tool calls — stays visible across the full turn
* Fixed `/rename` without args failing on resumed sessions whose last entry is a compact boundary
* Fixed stale "remote-control is active" status lines from prior sessions appearing after `--resume`/`--continue`
* Fixed stale `installed_plugins.json` entries pointing at deleted cache directories polluting PATH
* Fixed MCP stdio servers receiving corrupted arguments when `CLAUDE_CODE_SHELL_PREFIX` is set and an argument contains spaces or shell metacharacters
* Fixed sub-agent progress summaries missing the prompt cache (\~3× `cache_creation` reduction)
* Fixed `/plugin update` never detecting new versions of npm-sourced plugins
* Fixed sub-agent summaries firing repeatedly while a sub-agent's transcript is static, capping worst-case token cost on idle sub-agents
* Headless `--output-format stream-json`: `init.plugin_errors` now includes `--plugin-dir` load failures in addition to dependency demotions

### 2.1.126 (May 1, 2026)

* The `/model` picker now lists models from your gateway's `/v1/models` endpoint when `ANTHROPIC_BASE_URL` points at an Anthropic-compatible gateway
* * Added `claude project purge [path]` to delete all Claude Code state for a project (transcripts, tasks, file history, config entry) — supports `--dry-run`, `-y/--yes`, `-i/--interactive`, and `--all`
* `--dangerously-skip-permissions` now bypasses prompts for writes to `.claude/`, `.git/`, `.vscode/`, shell config files, and other previously-protected paths (catastrophic removal commands still prompt as a safety net)
* `claude auth login` now accepts the OAuth code pasted into the terminal when the browser callback can't reach localhost (WSL2, SSH, containers)
* `claude_code.skill_activated` OpenTelemetry event now fires for user-typed slash commands and carries a new `invocation_trigger` attribute (`"user-slash"`, `"claude-proactive"`, or `"nested-skill"`)
* Auto mode: the spinner now turns red when a permission check stalls, instead of looking like the tool is running
* Host-managed deployments (`CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST`) no longer auto-disable analytics on Bedrock/Vertex/Foundry
* Windows: PowerShell 7 installed via the Microsoft Store, MSI without PATH, or `.NET global tool` is now detected
* Windows: when the PowerShell tool is enabled, Claude now treats PowerShell as the primary shell instead of defaulting to Bash
* Read tool: removed the per-file malware-assessment reminder that could cause spurious refusals and "this is not malware" commentary on legacy models
* **Security:** Fixed `allowManagedDomainsOnly` / `allowManagedReadPathsOnly` being ignored when a higher-priority managed-settings source lacked a `sandbox` block
* Fixed pasting an image larger than 2000px breaking the session — images are now downscaled on paste, and oversized images in history are automatically removed and the request retried
* Fixed showing the login screen for "OAuth not allowed for organization" errors — now shows guidance to contact your admin
* Fixed OAuth login failing with timeout on slow or proxied connections, in IPv6-only devcontainers, and when the browser callback can't reach localhost
* Fixed a rare race where a concurrent credential write could clear a valid OAuth refresh token
* Fixed API retry countdown sticking at "0s" instead of counting down between attempts
* Fixed "Stream idle timeout" error after waking Mac from sleep mid-request
* Fixed background and remote sessions falsely aborting with "Stream idle timeout" during long model thinking pauses
* Fixed a hang where the assistant could finish thinking but show no output after a run of empty turns
* Fixed overly fast trackpad scrolling in Cursor and VS Code 1.92–1.104 integrated terminals
* Fixed claude.ai MCP connectors being suppressed by manual servers stuck in needs-auth state
* Fixed Japanese/Korean/Chinese text rendering as garbled characters on Windows in no-flicker mode
* Fixed `Ctrl+L` clearing the prompt input — it now only forces a screen redraw, matching readline behavior
* Fixed deferred tools (WebSearch, WebFetch, etc.) not being available to skills with `context: fork` and other subagents on their first turn
* Fixed plan-mode tools being unavailable in interactive sessions launched with `--channels`
* Fixed `/plugin` Uninstall reporting "Enabled" instead of "Uninstalled"
* Bounded total size of file-modified reminders when a linter touches many files at once
* Fixed `/remote-control` retries appearing stuck on "connecting…" — each retry now shows its result
* Fixed Remote Control failure notification not showing the error reason for initial connection failures
* Windows: clipboard writes no longer expose copied content in process command-line arguments visible to EDR/SIEM telemetry; also fixes >22KB selections not reaching the clipboard
* PowerShell tool: bare `--` (e.g. `git diff -- file`) is no longer mis-flagged as the `--%` stop-parsing token
* Fixed Agent SDK hang when the model emits a malformed tool name in a parallel tool call batch

### 2.1.123 (April 29, 2026)

* Fixed OAuth authentication failing with a 401 retry loop when `CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1` is set

### 2.1.122 (April 28, 2026)

* Added `ANTHROPIC_BEDROCK_SERVICE_TIER` environment variable to select a Bedrock service tier (`default`, `flex`, or `priority`), sent as the `X-Amzn-Bedrock-Service-Tier` header
* Pasting a PR URL into the `/resume` search box now finds the session that created that PR (GitHub, GitHub Enterprise, GitLab, and Bitbucket)
* `/mcp` now shows claude.ai connectors hidden by a manually-added server with the same URL, with a hint to remove the duplicate
* Clarified the `/mcp` message shown when an MCP server is still unauthorized after the browser sign-in flow
* OpenTelemetry: numeric attributes on `api_request`/`api_error` log events are now emitted as numbers, not strings
* OpenTelemetry: added `claude_code.at_mention` log event for `@`-mention resolution
* Fixed `/branch` producing forks that fail with "tool\_use ids were found without tool\_result blocks" when the source session contained entries from rewound timelines
* Fixed `/model` not showing the Effort option for Bedrock application inference profile ARNs, and those ARNs not receiving `output_config.effort`
* Fixed Vertex AI / Bedrock returning `invalid_request_error: output_config: Extra inputs are not permitted` on session-title generation and other structured-output queries
* Fixed Vertex AI `count_tokens` endpoint returning 400 errors for users behind proxy gateways
* Fixed `spinnerTipsOverride.excludeDefault` not suppressing the time-based spinner tips
* Fixed ToolSearch missing MCP tools that connected after session start in nonblocking mode
* Fixed `!exit` / `!quit` in bash mode terminating the CLI instead of running as a shell command
* Fixed images sent to newer models being resized to 2576px per side instead of the correct 2000px maximum
* Fixed remote control session idle status redrawing twice per second, which could flood `tmux -CC` control pipes and pause the terminal
* Fixed assistant messages appearing blank in some sessions due to a stale view preference
* Fixed a malformed hooks entry in `settings.json` no longer invalidating the entire file
* Voice mode: keybindings bound to Caps Lock now show an error since terminals don't deliver Caps Lock as a key event

### 2.1.121 (April 28, 2026)

* Added `alwaysLoad` option to MCP server config — when `true`, all tools from that server skip tool-search deferral and are always available
* Added `claude plugin prune` to remove orphaned auto-installed plugin dependencies; `plugin uninstall --prune` cascades
* Added a type-to-filter search box to `/skills` so you can find a skill in long lists without scrolling
* PostToolUse hooks can now replace tool output for all tools via `hookSpecificOutput.updatedToolOutput` (previously MCP-only)
* Fullscreen mode: typing into the prompt no longer jumps scroll back to the bottom after you've scrolled up to read earlier output
* Dialogs that overflow the terminal are now scrollable with arrow keys, PgUp/PgDn, home/end, and mouse wheel in both fullscreen and non-fullscreen modes
* Clicking any line of a long URL that wraps across rows in fullscreen mode now opens the full URL
* SDK and `claude -p`: `CLAUDE_CODE_FORK_SUBAGENT=1` now works in non-interactive sessions
* `--dangerously-skip-permissions` no longer prompts for writes to `.claude/skills/`, `.claude/agents/`, and `.claude/commands/`
* `/terminal-setup` now enables iTerm2's "Applications in terminal may access clipboard" setting so `/copy` works, including from tmux
* MCP servers that hit a transient error during startup now auto-retry up to 3 times instead of staying disconnected
* The terminal tab session title is now generated in your configured `language` setting
* Claude.ai connectors with the same upstream URL are now deduplicated instead of appearing as duplicates
* Vertex AI: support X.509 certificate-based Workload Identity Federation (mTLS ADC)
* Faster startup after upgrading: removed the Recent Activity panel from the release-notes splash
* LSP diagnostic summaries now expand on click/ctrl+o and show the expand hint
* SDK: `mcp_authenticate` now supports `redirectUri` for custom scheme completion and claude.ai connectors
* OpenTelemetry: added `stop_reason`, `gen_ai.response.finish_reasons`, and `user_system_prompt` (gated behind `OTEL_LOG_USER_PROMPTS`) to LLM request spans
* \[VSCode] Voice dictation now respects the `accessibility.voice.speechLanguage` setting when no Claude Code language is configured
* \[VSCode] `/context` now opens a native token usage dialog
* Fixed unbounded memory growth (multi-GB RSS) when processing many images in a session
* Fixed `/usage` leaking up to \~2GB of memory on machines with large transcript histories
* Fixed memory leak when long-running tools fail to emit a clear progress event
* Fixed Bash tool becoming permanently unusable when the directory Claude was started in is deleted or moved mid-session
* Fixed `--resume` crashing on startup in external builds
* Fixed `--resume` failing on large sessions when a transcript line was corrupted by an unclean shutdown — the corrupt line is now skipped
* Fixed `thinking.type.enabled is not supported` error when using Bedrock application inference profile ARNs
* Fixed Microsoft 365 MCP OAuth failing with duplicate or unsupported `prompt` parameter
* Fixed scrollback duplication when pressing Ctrl+L or triggering a redraw in non-fullscreen mode on tmux, GNOME Terminal, Windows Terminal, and Konsole
* Fixed claude.ai MCP connectors silently disappearing when the connector-list fetch hits a transient auth error at startup
* Fixed "Always allow" rules for built-in tools in remote sessions not surviving worker restarts
* Fixed `NO_PROXY` not being respected for all HTTP clients when set via `managed-settings.json` under the native build
* Fixed managed settings approval prompt exiting the session even when accepted — now applies settings and continues
* Fixed `/usage` returning "rate limited" after a stale OAuth token — now refreshes automatically
* Fixed invalid legacy enum values in `settings.json` invalidating the entire settings file
* Fixed `/usage` dialog content being clipped when no-flicker mode is off
* Fixed `/focus` showing "Unknown command" when the fullscreen renderer is off — now explains how to enable it
* Fixed embedded grep/find/rg shell wrappers failing when the running binary is deleted mid-session — now falls back to installed tools
* Reduced peak file descriptor usage during `find` in the Bash tool on large directory trees

### 2.1.120 (April 28, 2026)

* Windows: Git for Windows (Git Bash) is no longer required — when absent, Claude Code uses PowerShell as the shell tool
* Added `claude ultrareview [target]` subcommand to run `/ultrareview` non-interactively from CI or scripts — prints findings to stdout (`--json` for raw output) and exits 0 on completion or 1 on failure
* Skills can now reference the current effort level with `${CLAUDE_EFFORT}` in their content
* Set `AI_AGENT` environment variable for subprocesses so `gh` can attribute traffic to Claude Code
* Spinner tips that recommend installing the desktop app or creating skills/agents are now hidden when you already have them
* Show a "use PgUp/PgDn to scroll" hint when the terminal sends arrow keys instead of scroll events
* Faster session start when you have many claude.ai connectors configured but not authorized
* The auto mode denial message now links to the configuration docs
* `claude plugin validate` now accepts `$schema`, `version`, and `description` at the top level of `marketplace.json` and `$schema` in `plugin.json`
* Auto-compact in auto mode now displays `auto` (lowercase, no token count) instead of a misleading token value
* Fixed pressing Esc during a stdio MCP tool call closing the entire server connection (regression in 2.1.105)
* Fixed `/rewind` and other interactive overlays not responding to keyboard input after launching with `claude --resume`
* Fixed terminal scrollback duplication in non-fullscreen mode (resize, dialog dismiss, long sessions)
* Fixed `DISABLE_TELEMETRY` / `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` not suppressing usage metrics telemetry for API and enterprise users
* Fixed false-positive "Dangerous rm operation" permission prompts in auto mode for multi-line bash commands containing both a pipe and a redirect
* Fixed long selection menus clipping below the terminal in fullscreen mode — the focused option now stays on screen as you scroll
* Fixed Write tool output collapsing instead of expanding when clicking "+N lines" in fullscreen
* Fixed slash command picker jumping while typing, and improved highlight to only match contiguous substrings in blue
* Fixed `/plugin` marketplace failing to load when one entry uses an unrecognized source format — that entry is shown but installing it prompts you to update
* \[VSCode] `/usage` now opens the native Account & Usage dialog instead of returning plain-text session cost
* \[VSCode] Voice dictation now respects the `language` setting in `~/.claude/settings.json`
* Fixed `find` in the Bash tool exhausting open file descriptors on large directory trees, causing host-wide crashes (macOS/Linux native builds)

### 2.1.119 (April 23, 2026)

* `/config` settings (theme, editor mode, verbose, etc.) now persist to `~/.claude/settings.json` and participate in project/local/policy override precedence
* Added `prUrlTemplate` setting to point the footer PR badge at a custom code-review URL instead of github.com
* Added `CLAUDE_CODE_HIDE_CWD` environment variable to hide the working directory in the startup logo
* `--from-pr` now accepts GitLab merge-request, Bitbucket pull-request, and GitHub Enterprise PR URLs
* `--print` mode now honors the agent's `tools:` and `disallowedTools:` frontmatter, matching interactive-mode behavior
* `--agent <name>` now honors the agent definition's `permissionMode` for built-in agents
* PowerShell tool commands can now be auto-approved in permission mode, matching Bash behavior
* Hooks: `PostToolUse` and `PostToolUseFailure` hook inputs now include `duration_ms` (tool execution time, excluding permission prompts and PreToolUse hooks)
* Subagent and SDK MCP server reconfiguration now connects servers in parallel instead of serially
* Plugins pinned by another plugin's version constraint now auto-update to the highest satisfying git tag
* Vim mode: Esc in INSERT no longer pulls a queued message back into the input; press Esc again to interrupt
* Slash command suggestions now highlight the characters that matched your query
* Slash command picker now wraps long descriptions onto a second line instead of truncating
* `owner/repo#N` shorthand links in output now use your git remote's host instead of always pointing at github.com
* Security: `blockedMarketplaces` now correctly enforces `hostPattern` and `pathPattern` entries
* OpenTelemetry: `tool_result` and `tool_decision` events now include `tool_use_id`; `tool_result` also includes `tool_input_size_bytes`
* Status line: stdin JSON now includes `effort.level` and `thinking.enabled`
* Fixed pasting CRLF content (Windows clipboards, Xcode console) inserting an extra blank line between every line
* Fixed multi-line paste losing newlines in terminals using kitty keyboard protocol sequences inside bracketed paste
* Fixed Glob and Grep tools disappearing on native macOS/Linux builds when the Bash tool is denied via permissions
* Fixed scrolling up in fullscreen mode snapping back to the bottom every time a tool finishes
* Fixed MCP HTTP connections failing with "Invalid OAuth error response" when servers returned non-JSON bodies for OAuth discovery requests
* Fixed Rewind overlay showing "(no prompt)" for messages with image attachments
* Fixed auto mode overriding plan mode with conflicting "Execute immediately" instructions
* Fixed async `PostToolUse` hooks that emit no response payload writing empty entries to the session transcript
* Fixed spinner staying on when a subagent task notification is orphaned in the queue
* Tool search is now disabled by default on Vertex AI to avoid an unsupported beta header error (opt in with `ENABLE_TOOL_SEARCH`)
* Fixed `@`-file Tab completion replacing the entire prompt when used inside a slash command with an absolute path
* Fixed a stray `p` character appearing at the prompt on startup in macOS Terminal.app via Docker or SSH
* Fixed `${ENV_VAR}` placeholders in `headers` for HTTP/SSE/WebSocket MCP servers not being substituted before requests
* Fixed MCP OAuth client secret stored via `--client-secret` not being sent during token exchange for servers requiring `client_secret_post`
* Fixed `/skills` Enter key closing the dialog instead of pre-filling `/<skill-name>` in the prompt
* Fixed `/agents` detail view mislabeling built-in tools unavailable to subagents as "Unrecognized"
* Fixed MCP servers from plugins not spawning on Windows when the plugin cache was incomplete
* Fixed `/export` showing the current default model instead of the model the conversation actually used
* Fixed verbose output setting not persisting after restart
* Fixed `/usage` progress bars overlapping with their "Resets …" labels
* Fixed plugin MCP servers failing when `${user_config.*}` references an optional field left blank
* Fixed list items containing a sentence-final number wrapping the number onto its own line
* Fixed `/plan` and `/plan open` not acting on the existing plan when entering plan mode
* Fixed skills invoked before auto-compaction being re-executed against the next user message
* Fixed `/reload-plugins` and `/doctor` reporting load errors for disabled plugins
* Fixed Agent tool with `isolation: "worktree"` reusing stale worktrees from prior sessions
* Fixed disabled MCP servers appearing as "failed" in `/status`
* Fixed `TaskList` returning tasks in arbitrary filesystem order instead of sorted by ID
* Fixed spurious "GitHub API rate limit exceeded" hints when `gh` output contained PR titles mentioning "rate limit"
* Fixed SDK/bridge `read_file` not correctly enforcing size cap on growing files
* Fixed PR not linked to session when working in a git worktree
* Fixed `/doctor` warning about MCP server entries overridden by a higher-precedence scope
* Windows: removed false-positive "Windows requires 'cmd /c' wrapper" MCP config warning
* \[VSCode] Fixed voice dictation's first recording producing nothing on macOS while the microphone permission prompt is showing

### 2.1.118 (April 23, 2026)

* Added vim visual mode (`v`) and visual-line mode (`V`) with selection, operators, and visual feedback
* Merged `/cost` and `/stats` into `/usage` — both remain as typing shortcuts that open the relevant tab
* Create and switch between named custom themes from `/theme`, or hand-edit JSON files in `~/.claude/themes/`; plugins can also ship themes via a `themes/` directory
* Hooks can now invoke MCP tools directly via `type: "mcp_tool"`
* Added `DISABLE_UPDATES` env var to completely block all update paths including manual `claude update` — stricter than `DISABLE_AUTOUPDATER`
* WSL on Windows can now inherit Windows-side managed settings via the `wslInheritsWindowsSettings` policy key
* Auto mode: include `"$defaults"` in `autoMode.allow`, `autoMode.soft_deny`, or `autoMode.environment` to add custom rules alongside the built-in list instead of replacing it
* Added a "Don't ask again" option to the auto mode opt-in prompt
* Added `claude plugin tag` to create release git tags for plugins with version validation
* `--continue`/`--resume` now find sessions that added the current directory via `/add-dir`
* `/color` now syncs the session accent color to claude.ai/code when Remote Control is connected
* The `/model` picker now honors `ANTHROPIC_DEFAULT_*_MODEL_NAME`/`_DESCRIPTION` overrides when using a custom `ANTHROPIC_BASE_URL` gateway
* When auto-update skips a plugin due to another plugin's version constraint, the skip now appears in `/doctor` and the `/plugin` Errors tab
* Fixed `/mcp` menu hiding OAuth Authenticate/Re-authenticate actions for servers configured with `headersHelper`, and HTTP/SSE MCP servers with custom headers being stuck in "needs authentication" after a transient 401
* Fixed MCP servers whose OAuth token response omits `expires_in` requiring re-authentication every hour
* Fixed MCP step-up authorization silently refreshing instead of prompting for re-consent when the server's `insufficient_scope` 403 names a scope the current token already has
* Fixed an unhandled promise rejection when an MCP server's OAuth flow times out or is cancelled
* Fixed MCP OAuth refresh proceeding without its cross-process lock under contention
* Fixed macOS keychain race where a concurrent MCP token refresh could overwrite a freshly-refreshed OAuth token, causing unexpected "Please run /login" prompts
* Fixed OAuth token refresh failing when the server revokes a token before its local expiry time
* Fixed credential save crash on Linux/Windows corrupting `~/.claude/.credentials.json`
* Fixed `/login` having no effect in a session launched with `CLAUDE_CODE_OAUTH_TOKEN` — the env token is now cleared so disk credentials take effect
* Fixed unreadable text in the "new messages" scroll pill and `/plugin` badges
* Fixed plan acceptance dialog offering "auto mode" instead of "bypass permissions" when running with `--dangerously-skip-permissions`
* Fixed agent-type hooks failing with "Messages are required for agent hooks" when configured for events other than `Stop` or `SubagentStop`
* Fixed `prompt` hooks re-firing on tool calls made by an agent-hook verifier subagent
* Fixed `/fork` writing the full parent conversation to disk per fork — now writes a pointer and hydrates on read
* Fixed Alt+K / Alt+X / Alt+^ / Alt+\_ freezing keyboard input
* Fixed connecting to a remote session overwriting your local `model` setting in `~/.claude/settings.json`
* Fixed typeahead showing "No commands match" error when pasting file paths that start with `/`
* Fixed `plugin install` on an already-installed plugin not re-resolving a dependency installed at the wrong version
* Fixed unhandled errors from file watcher on invalid paths or fd exhaustion
* Fixed Remote Control sessions getting archived on transient CCR initialization blips during JWT refresh
* Fixed subagents resumed via `SendMessage` not restoring the explicit `cwd` they were spawned with

### 2.1.117 (April 22, 2026)

* Forked subagents can now be enabled on external builds by setting `CLAUDE_CODE_FORK_SUBAGENT=1`
* Agent frontmatter `mcpServers` are now loaded for main-thread agent sessions via `--agent`
* Improved `/model`: selections now persist across restarts even when the project pins a different model, and the startup header shows when the active model comes from a project or managed-settings pin
* The `/resume` command now offers to summarize stale, large sessions before re-reading them, matching the existing `--resume` behavior
* Faster startup when both local and claude.ai MCP servers are configured (concurrent connect now default)
* `plugin install` on an already-installed plugin now installs any missing dependencies instead of stopping at "already installed"
* Plugin dependency errors now say "not installed" with an install hint, and `claude plugin marketplace add` now auto-resolves missing dependencies from configured marketplaces
* Managed-settings `blockedMarketplaces` and `strictKnownMarketplaces` are now enforced on plugin install, update, refresh, and autoupdate
* Advisor Tool (experimental): dialog now carries an "experimental" label, learn-more link, and startup notification when enabled; sessions no longer get stuck with "Advisor tool result content could not be processed" errors on every prompt and `/compact`
* The `cleanupPeriodDays` retention sweep now also covers `~/.claude/tasks/`, `~/.claude/shell-snapshots/`, and `~/.claude/backups/`
* OpenTelemetry: `user_prompt` events now include `command_name` and `command_source` for slash commands; `cost.usage`, `token.usage`, `api_request`, and `api_error` now include an `effort` attribute when the model supports effort levels. Custom/MCP command names are redacted unless `OTEL_LOG_TOOL_DETAILS=1` is set
* Native builds on macOS and Linux: the `Glob` and `Grep` tools are replaced by embedded `bfs` and `ugrep` available through the Bash tool — faster searches without a separate tool round-trip (Windows and npm-installed builds unchanged)
* Windows: cached `where.exe` executable lookups per process for faster subprocess launches
* Default effort for Pro/Max subscribers on Opus 4.6 and Sonnet 4.6 is now `high` (was `medium`)
* Fixed Plain-CLI OAuth sessions dying with "Please run /login" when the access token expires mid-session — the token is now refreshed reactively on 401
* Fixed `WebFetch` hanging on very large HTML pages by truncating input before HTML-to-markdown conversion
* Fixed a crash when a proxy returns HTTP 204 No Content — now surfaces a clear error instead of a `TypeError`
* Fixed `/login` having no effect when launched with `CLAUDE_CODE_OAUTH_TOKEN` env var and that token expires
* Fixed prompt-input undo (`Ctrl+_`) doing nothing immediately after typing, and skipping a state on each undo step
* Fixed `NO_PROXY` not being respected for remote API requests when running under Bun
* Fixed rare spurious escape/return triggers when key names arrive as coalesced text over slow connections
* Fixed SDK `reload_plugins` reconnecting all user MCP servers serially
* Fixed Bedrock application-inference-profile requests failing with 400 when backed by Opus 4.7 with thinking disabled
* Fixed MCP `elicitation/create` requests auto-cancelling in print/SDK mode when the server finishes connecting mid-turn
* Fixed subagents running a different model than the main agent incorrectly flagging file reads with a malware warning
* Fixed idle re-render loop when background tasks are present, reducing memory growth on Linux
* \[VSCode] Fixed "Manage Plugins" panel breaking when multiple large marketplaces are configured
* Fixed Opus 4.7 sessions showing inflated `/context` percentages and autocompacting too early — Claude Code was computing against a 200K context window instead of Opus 4.7's native 1M

### 2.1.116 (April 20, 2026)

* `/resume` on large sessions is significantly faster (up to 67% on 40MB+ sessions) and handles sessions with many dead-fork entries more efficiently
* Faster MCP startup when multiple stdio servers are configured; `resources/templates/list` is now deferred to first `@`-mention
* Smoother fullscreen scrolling in VS Code, Cursor, and Windsurf terminals — `/terminal-setup` now configures the editor's scroll sensitivity
* Thinking spinner now shows progress inline ("still thinking", "thinking more", "almost done thinking"), replacing the separate hint row
* `/config` search now matches option values (e.g. searching "vim" finds the Editor mode setting)
* `/doctor` can now be opened while Claude is responding, without waiting for the current turn to finish
* `/reload-plugins` and background plugin auto-update now auto-install missing plugin dependencies from marketplaces you've already added
* Bash tool now surfaces a hint when `gh` commands hit GitHub's API rate limit, so agents can back off instead of retrying
* The Usage tab in Settings now shows your 5-hour and weekly usage immediately and no longer fails when the usage endpoint is rate-limited
* Agent frontmatter `hooks:` now fire when running as a main-thread agent via `--agent`
* Slash command menu now shows "No commands match" when your filter has zero results, instead of disappearing
* Security: sandbox auto-allow no longer bypasses the dangerous-path safety check for `rm`/`rmdir` targeting `/`, `$HOME`, or other critical system directories
* Claude Code and installer now use `https://downloads.claude.ai/claude-code-releases` instead of `https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases`
* Fixed Devanagari and other Indic scripts rendering with broken column alignment in the terminal UI
* Fixed Ctrl+- not triggering undo in terminals using the Kitty keyboard protocol (iTerm2, Ghostty, kitty, WezTerm, Windows Terminal)
* Fixed Cmd+Left/Right not jumping to line start/end in terminals that use the Kitty keyboard protocol (Warp fullscreen, kitty, Ghostty, WezTerm)
* Fixed Ctrl+Z hanging the terminal when Claude Code is launched via a wrapper process (e.g. `npx`, `bun run`)
* Fixed scrollback duplication in inline mode where resizing the terminal or large output bursts would repeat earlier conversation history
* Fixed modal search dialogs overflowing the screen at short terminal heights, hiding the search box and keyboard hints
* Fixed scattered blank cells and disappearing composer chrome in the VS Code integrated terminal during scrolling
* Fixed an intermittent API 400 error related to cache control TTL ordering that could occur when a parallel request completed during request setup
* Fixed `/branch` rejecting conversations with transcripts larger than 50MB
* Fixed `/resume` silently showing an empty conversation on large session files instead of reporting the load error
* Fixed `/plugin` Installed tab showing the same item twice when it appears under Needs attention or Favorites
* Fixed `/update` and `/tui` not working after entering a worktree mid-session

### 2.1.114 (April 18, 2026)

* Fixed a crash in the permission dialog when an agent teams teammate requested tool permission

### 2.1.113 (April 17, 2026)

* Changed the CLI to spawn a native Claude Code binary (via a per-platform optional dependency) instead of bundled JavaScript
* Added `sandbox.network.deniedDomains` setting to block specific domains even when a broader `allowedDomains` wildcard would otherwise permit them
* Fullscreen mode: Shift+↑/↓ now scrolls the viewport when extending a selection past the visible edge
* `Ctrl+A` and `Ctrl+E` now move to the start/end of the current logical line in multiline input, matching readline behavior
* Windows: `Ctrl+Backspace` now deletes the previous word
* Long URLs in responses and bash output stay clickable when they wrap across lines (in terminals with OSC 8 hyperlinks)
* Improved `/loop`: pressing Esc now cancels pending wakeups, and wakeups display as "Claude resuming /loop wakeup" for clarity
* `/extra-usage` now works from Remote Control (mobile/web) clients
* Remote Control clients can now query `@`-file autocomplete suggestions
* Improved `/ultrareview`: faster launch with parallelized checks, diffstat in the launch dialog, and animated launching state
* Subagents that stall mid-stream now fail with a clear error after 10 minutes instead of hanging silently
* Bash tool: multi-line commands whose first line is a comment now show the full command in the transcript, closing a UI-spoofing vector
* Running `cd <current-directory> && git …` no longer triggers a permission prompt when the `cd` is a no-op
* Security: on macOS, `/private/{etc,var,tmp,home}` paths are now treated as dangerous removal targets under `Bash(rm:*)` allow rules
* Security: Bash deny rules now match commands wrapped in `env`/`sudo`/`watch`/`ionice`/`setsid` and similar exec wrappers
* Security: `Bash(find:*)` allow rules no longer auto-approve `find -exec`/`-delete`
* Fixed MCP concurrent-call timeout handling where a message for one tool call could silently disarm another call's watchdog
* Fixed Cmd-backspace / `Ctrl+U` to once again delete from the cursor to the start of the line
* Fixed markdown tables breaking when a cell contains an inline code span with a pipe character
* Fixed session recap auto-firing while composing unsent text in the prompt
* Fixed `/copy` "Full response" not aligning markdown table columns for pasting into GitHub, Notion, or Slack
* Fixed messages typed while viewing a running subagent being hidden from its transcript and misattributed to the parent AI
* Fixed Bash `dangerouslyDisableSandbox` running commands outside the sandbox without a permission prompt
* Fixed `/effort auto` confirmation — now says "Effort level set to max" to match the status bar label
* Fixed the "copied N chars" toast overcounting emoji and other multi-code-unit characters
* Fixed `/insights` crashing with `EBUSY` on Windows
* Fixed exit confirmation dialog mislabeling one-shot scheduled tasks as recurring — now shows a countdown
* Fixed slash/@ completion menu not sitting flush against the prompt border in fullscreen mode
* Fixed `CLAUDE_CODE_EXTRA_BODY` `output_config.effort` causing 400 errors on subagent calls to models that don't support effort and on Vertex AI
* Fixed prompt cursor disappearing when `NO_COLOR` is set
* Fixed `ToolSearch` ranking so pasted MCP tool names surface the actual tool instead of description-matching siblings
* Fixed compacting a resumed long-context session failing with "Extra usage is required for long context requests"
* Fixed `plugin install` succeeding when a dependency version conflicts with an already-installed plugin — now reports `range-conflict`
* Fixed "Refine with Ultraplan" not showing the remote session URL in the transcript
* Fixed SDK image content blocks that fail to process crashing the session — now degrade to a text placeholder
* Fixed Remote Control sessions not streaming subagent transcripts
* Fixed Remote Control sessions not being archived when Claude Code exits
* Fixed `thinking.type.enabled is not supported` 400 error when using Opus 4.7 via a Bedrock Application Inference Profile ARN

### 2.1.112 (April 16, 2026)

* Fixed "claude-opus-4-7 is temporarily unavailable" for auto mode

### 2.1.111 (April 16, 2026)

* Claude Opus 4.7 xhigh is now available! Use /effort to tune speed vs. intelligence
* Auto mode is now available for Max subscribers when using Opus 4.7
* Added `xhigh` effort level for Opus 4.7, sitting between `high` and `max`. Available via `/effort`, `--effort`, and the model picker; other models fall back to `high`
* `/effort` now opens an interactive slider when called without arguments, with arrow-key navigation between levels and Enter to confirm
* Added "Auto (match terminal)" theme option that matches your terminal's dark/light mode — select it from `/theme`
* Added `/less-permission-prompts` skill — scans transcripts for common read-only Bash and MCP tool calls and proposes a prioritized allowlist for `.claude/settings.json`
* Added `/ultrareview` for running comprehensive code review in the cloud using parallel multi-agent analysis and critique — invoke with no arguments to review your current branch, or `/ultrareview ` to fetch and review a specific GitHub PR
* Auto mode no longer requires `--enable-auto-mode`
* Windows: PowerShell tool is progressively rolling out. Opt in or out with `CLAUDE_CODE_USE_POWERSHELL_TOOL`. On Linux and macOS, enable with `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` (requires `pwsh` on PATH)
* Read-only bash commands with glob patterns (e.g. `ls *.ts`) and commands starting with `cd <project-dir> &&` no longer trigger a permission prompt
* Suggest the closest matching subcommand when `claude <word>` is invoked with a near-miss typo (e.g. `claude udpate` → "Did you mean `claude update`?")
* Plan files are now named after your prompt (e.g. `fix-auth-race-snug-otter.md`) instead of purely random words
* Improved `/setup-vertex` and `/setup-bedrock` to show the actual `settings.json` path when `CLAUDE_CONFIG_DIR` is set, seed model candidates from existing pins on re-run, and offer a "with 1M context" option for supported models
* `/skills` menu now supports sorting by estimated token count — press `t` to toggle
* `Ctrl+U` now clears the entire input buffer (previously: delete to start of line); press `Ctrl+Y` to restore
* `Ctrl+L` now forces a full screen redraw in addition to clearing the prompt input
* Transcript view footer now shows `[` (dump to scrollback) and `v` (open in editor) shortcuts
* The "+N lines" marker for truncated long pastes is now a full-width rule for easier scanning
* Headless `--output-format stream-json` now includes `plugin_errors` on the init event when plugins are demoted for unsatisfied dependencies
* Added `OTEL_LOG_RAW_API_BODIES` environment variable to emit full API request and response bodies as OpenTelemetry log events for debugging
* Suppressed spurious decompression, network, and transient error messages that could appear in the TUI during normal operation
* Reverted the v2.1.110 cap on non-streaming fallback retries — it traded long waits for more outright failures during API overload
* Fixed terminal display tearing (random characters, drifting input) in iTerm2 + tmux setups when terminal notifications are sent
* Fixed `@` file suggestions re-scanning the entire project on every turn in non-git working directories, and showing only config files in freshly-initialized git repos with no tracked files
* Fixed LSP diagnostics from before an edit appearing after it, causing the model to re-read files it just edited
* Fixed tab-completing `/resume` immediately resuming an arbitrary titled session instead of showing the session picker
* Fixed `/context` grid rendering with extra blank lines between rows
* Fixed `/clear` dropping the session name set by `/rename`, causing statusline output to lose `session_name`
* Improved plugin error handling: dependency errors now distinguish conflicting, invalid, and overly complex version requirements; fixed stale resolved versions after `plugin update`; `plugin install` now recovers from interrupted prior installs
* Fixed Claude calling a non-existent `commit` skill and showing "Unknown skill: commit" for users without a custom `/commit` command
* Fixed 429 rate-limit errors on Bedrock/Vertex/Foundry referencing status.claude.com (it only covers Anthropic-operated providers)
* Fixed feedback surveys appearing back-to-back after dismissing one
* Fixed bare URLs in bash/PowerShell/MCP tool output being unclickable when the terminal wraps them across lines
* Windows: `CLAUDE_ENV_FILE` and SessionStart hook environment files now apply (previously a no-op)
* Windows: permission rules with drive-letter paths are now correctly root-anchored, and paths differing only by drive-letter case are recognized as the same path

### 2.1.110 (April 15, 2026)

* Added `/tui` command and `tui` setting — run `/tui fullscreen` to switch to flicker-free rendering in the same conversation
* Added push notification tool — Claude can send mobile push notifications when Remote Control and "Push when Claude decides" config are enabled
* Changed `Ctrl+O` to toggle between normal and verbose transcript only; focus view is now toggled separately with the new `/focus` command
* Added `autoScrollEnabled` config to disable conversation auto-scroll in fullscreen mode
* Added option to show Claude's last response as commented context in the `Ctrl+G` external editor (enable via `/config`)
* Improved `/plugin` Installed tab — items needing attention and favorites appear at the top, disabled items are hidden behind a fold, and `f` favorites the selected item
* Improved `/doctor` to warn when an MCP server is defined in multiple config scopes with different endpoints
* `--resume`/`--continue` now resurrects unexpired scheduled tasks
* `/context`, `/exit`, and `/reload-plugins` now work from Remote Control (mobile/web) clients
* Write tool now informs the model when you edit the proposed content in the IDE diff before accepting
* Bash tool now enforces the documented maximum timeout instead of accepting arbitrarily large values
* SDK/headless sessions now read `TRACEPARENT`/`TRACESTATE` from the environment for distributed trace linking
* Session recap is now enabled for users with telemetry disabled (Bedrock, Vertex, Foundry, `DISABLE_TELEMETRY`). Opt out via `/config` or `CLAUDE_CODE_ENABLE_AWAY_SUMMARY=0`.
* Fixed MCP tool calls hanging indefinitely when the server connection drops mid-response on SSE/HTTP transports
* Fixed non-streaming fallback retries causing multi-minute hangs when the API is unreachable
* Fixed session recap, local slash-command output, and other system status lines not appearing in focus mode
* Fixed high CPU usage in fullscreen when text is selected while a tool is running
* Fixed plugin install not honoring dependencies declared in `plugin.json` when the marketplace entry omits them; `/plugin` install now lists auto-installed dependencies
* Fixed skills with `disable-model-invocation: true` failing when invoked via `/<skill>` mid-message
* Fixed `--resume` sometimes showing the first prompt instead of the `/rename` name for sessions still running or exited uncleanly
* Fixed queued messages briefly appearing twice during multi-tool-call turns
* Fixed session cleanup not removing the full session directory including subagent transcripts
* Fixed dropped keystrokes after the CLI relaunches (e.g. `/tui`, provider setup wizards)
* Fixed garbled startup rendering in macOS Terminal.app and other terminals that don't support synchronized output
* Hardened "Open in editor" actions against command injection from untrusted filenames
* Fixed `PermissionRequest` hooks returning `updatedInput` not being re-checked against `permissions.deny` rules; `setMode:'bypassPermissions'` updates now respect `disableBypassPermissionsMode`
* Fixed `PreToolUse` hook `additionalContext` being dropped when the tool call fails
* Fixed stdio MCP servers that print stray non-JSON lines to stdout being disconnected on the first stray line (regression in 2.1.105)
* Fixed headless/SDK session auto-title firing an extra Haiku request when `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` or `CLAUDE_CODE_DISABLE_TERMINAL_TITLE` is set
* Fixed potential excessive memory allocation when piped (non-TTY) Ink output contains a single very wide line
* Fixed `/skills` menu not scrolling when the list overflows the modal in fullscreen mode
* Fixed Remote Control sessions showing a generic error instead of prompting for re-login when the session is too old
* Fixed Remote Control session renames from claude.ai not persisting the title to the local CLI session

### 2.1.109 (April 15, 2026)

* Improved the extended-thinking indicator with a rotating progress hint

### 2.1.108 (April 14, 2026)

* Added `ENABLE_PROMPT_CACHING_1H` env var to opt into 1-hour prompt cache TTL on API key, Bedrock, Vertex, and Foundry (`ENABLE_PROMPT_CACHING_1H_BEDROCK` is deprecated but still honored), and `FORCE_PROMPT_CACHING_5M` to force 5-minute TTL
* Added recap feature to provide context when returning to a session, configurable in `/config` and manually invocable with `/recap`; force with `CLAUDE_CODE_ENABLE_AWAY_SUMMARY` if telemetry disabled.
* The model can now discover and invoke built-in slash commands like `/init`, `/review`, and `/security-review` via the Skill tool
* `/undo` is now an alias for `/rewind`
* Improved `/model` to warn before switching models mid-conversation, since the next response re-reads the full history uncached
* Improved `/resume` picker to default to sessions from the current directory; press `Ctrl+A` to show all projects
* Improved error messages: server rate limits are now distinguished from plan usage limits; 5xx/529 errors show a link to status.claude.com; unknown slash commands suggest the closest match
* Reduced memory footprint for file reads, edits, and syntax highlighting by loading language grammars on demand
* Added "verbose" indicator when viewing the detailed transcript (`Ctrl+O`)
* Added a warning at startup when prompt caching is disabled via `DISABLE_PROMPT_CACHING*` environment variables
* Fixed paste not working in the `/login` code prompt (regression in 2.1.105)
* Fixed subscribers who set `DISABLE_TELEMETRY` falling back to 5-minute prompt cache TTL instead of 1 hour
* Fixed Agent tool prompting for permission in auto mode when the safety classifier's transcript exceeded its context window
* Fixed Bash tool producing no output when `CLAUDE_ENV_FILE` (e.g. `~/.zprofile`) ends with a `#` comment line
* Fixed `claude --resume <session-id>` losing the session's custom name and color set via `/rename`
* Fixed session titles showing placeholder example text when the first message is a short greeting
* Fixed terminal escape codes appearing as garbage text in the prompt input after `--teleport`
* Fixed `/feedback` retry: pressing Enter to resubmit after a failure now works without first editing the description
* Fixed `--teleport` and `--resume <id>` precondition errors (e.g. dirty git tree, session not found) exiting silently instead of showing the error message
* Fixed Remote Control session titles set in the web UI being overwritten by auto-generated titles after the third message
* Fixed `--resume` truncating sessions when the transcript contained a self-referencing message
* Fixed transcript write failures (e.g., disk full) being silently dropped instead of being logged
* Fixed diacritical marks (accents, umlauts, cedillas) being dropped from responses when the `language` setting is configured
* Fixed policy-managed plugins never auto-updating when running from a different project than where they were first installed

### 2.1.107 (April 14, 2026)

* Show thinking hints sooner during long operations

### 2.1.105 (April 13, 2026)

* Added `path` parameter to the `EnterWorktree` tool to switch into an existing worktree of the current repository
* Added PreCompact hook support: hooks can now block compaction by exiting with code 2 or returning `{"decision":"block"}`
* Added background monitor support for plugins via a top-level `monitors` manifest key that auto-arms at session start or on skill invoke
* `/proactive` is now an alias for `/loop`
* Improved stalled API stream handling: streams now abort after 5 minutes of no data and retry non-streaming instead of hanging indefinitely
* Improved network error messages: connection errors now show a retry message immediately instead of a silent spinner
* Improved file write display: long single-line writes (e.g. minified JSON) are now truncated in the UI instead of paginating across many screens
* Improved `/doctor` layout with status icons; press `f` to have Claude fix reported issues
* Improved `/config` labels and descriptions for clarity
* Improved skill description handling: raised the listing cap from 250 to 1,536 characters and added a startup warning when descriptions are truncated
* Improved `WebFetch` to strip `<style>` and `<script>` contents from fetched pages so CSS-heavy pages no longer exhaust the content budget before reaching actual text
* Improved stale agent worktree cleanup to remove worktrees whose PR was squash-merged instead of keeping them indefinitely
* Improved MCP large-output truncation prompt to give format-specific recipes (e.g. `jq` for JSON, computed Read chunk sizes for text)
* Fixed images attached to queued messages (sent while Claude is working) being dropped
* Fixed screen going blank when the prompt input wraps to a second line in long conversations
* Fixed leading whitespace getting copied when selecting multi-line assistant responses in fullscreen mode
* Fixed leading whitespace being trimmed from assistant messages, breaking ASCII art and indented diagrams
* Fixed garbled bash output when commands print clickable file links (e.g. Python `rich`/`loguru` logging)
* Fixed alt+enter not inserting a newline in terminals using ESC-prefix alt encoding, and Ctrl+J not inserting a newline (regression in 2.1.100)
* Fixed duplicate "Creating worktree" text in EnterWorktree/ExitWorktree tool display
* Fixed queued user prompts disappearing from focus mode
* Fixed one-shot scheduled tasks re-firing repeatedly when the file watcher missed the post-fire cleanup
* Fixed inbound channel notifications being silently dropped after the first message for Team/Enterprise users
* Fixed marketplace plugins with `package.json` and lockfile not having dependencies installed automatically after install/update
* Fixed marketplace auto-update leaving the official marketplace in a broken state when a plugin process holds files open during the update
* Fixed "Resume this session with..." hint not printing on exit after `/resume`, `--worktree`, or `/branch`
* Fixed feedback survey shortcut keys firing when typed at the end of a longer prompt
* Fixed stdio MCP server emitting malformed (non-JSON) output hanging the session instead of failing fast with "Connection closed"
* Fixed MCP tools missing on the first turn of headless/remote-trigger sessions when MCP servers connect asynchronously
* Fixed `/model` picker on AWS Bedrock in non-US regions persisting invalid `us.*` model IDs to `settings.json` when inference profile discovery is still in-flight
* Fixed 429 rate-limit errors showing a raw JSON dump instead of a clean message for API-key, Bedrock, and Vertex users
* Fixed crash on resume when session contains malformed text blocks
* Fixed `/help` dropping the tab bar, Shortcuts heading, and footer at short terminal heights
* Fixed malformed keybinding entry values in `keybindings.json` being silently loaded instead of rejected with a clear error
* Fixed `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` in one project's settings permanently disabling usage metrics for all projects on the machine
* Fixed washed-out 16-color palette when using Ghostty, Kitty, Alacritty, WezTerm, foot, rio, or Contour over SSH/mosh
* Fixed Bash tool suggesting `acceptEdits` permission mode when exiting plan mode would downgrade from a higher permission level

### 2.1.101 (April 10, 2026)

* Added `/team-onboarding` command to generate a teammate ramp-up guide from your local Claude Code usage
* Added OS CA certificate store trust by default, so enterprise TLS proxies work without extra setup (set `CLAUDE_CODE_CERT_STORE=bundled` to use only bundled CAs)
* `/ultraplan` and other remote-session features now auto-create a default cloud environment instead of requiring web setup first
* Improved brief mode to retry once when Claude responds with plain text instead of a structured message
* Improved focus mode: Claude now writes more self-contained summaries since it knows you only see its final message
* Improved tool-not-available errors to explain why and how to proceed when the model calls a tool that exists but isn't available in the current context
* Improved rate-limit retry messages to show which limit was hit and when it resets instead of an opaque seconds countdown
* Improved refusal error messages to include the API-provided explanation when available
* Improved `claude -p --resume <name>` to accept session titles set via `/rename` or `--name`
* Improved settings resilience: an unrecognized hook event name in `settings.json` no longer causes the entire file to be ignored
* Improved plugin hooks from plugins force-enabled by managed settings to run when `allowManagedHooksOnly` is set
* Improved `/plugin` and `claude plugin update` to show a warning when the marketplace could not be refreshed, instead of silently reporting a stale version
* Improved plan mode to hide the "Refine with Ultraplan" option when the user's org or auth setup can't reach Claude Code on the web
* Improved beta tracing to honor `OTEL_LOG_USER_PROMPTS`, `OTEL_LOG_TOOL_DETAILS`, and `OTEL_LOG_TOOL_CONTENT`; sensitive span attributes are no longer emitted unless opted in
* Improved SDK `query()` to clean up subprocess and temp files when consumers `break` from `for await` or use `await using`
* Fixed a command injection vulnerability in the POSIX `which` fallback used by LSP binary detection
* Fixed a memory leak where long sessions retained dozens of historical copies of the message list in the virtual scroller
* Fixed `--resume`/`--continue` losing conversation context on large sessions when the loader anchored on a dead-end branch instead of the live conversation
* Fixed `--resume` chain recovery bridging into an unrelated subagent conversation when a subagent message landed near a main-chain write gap
* Fixed a crash on `--resume` when a persisted Edit/Write tool result was missing its `file_path`
* Fixed a hardcoded 5-minute request timeout that aborted slow backends (local LLMs, extended thinking, slow gateways) regardless of `API_TIMEOUT_MS`
* Fixed `permissions.deny` rules not overriding a PreToolUse hook's `permissionDecision: "ask"` — previously the hook could downgrade a deny into a prompt
* Fixed `--setting-sources` without `user` causing background cleanup to ignore `cleanupPeriodDays` and delete conversation history older than 30 days
* Fixed Bedrock SigV4 authentication failing with 403 when `ANTHROPIC_AUTH_TOKEN`, `apiKeyHelper`, or `ANTHROPIC_CUSTOM_HEADERS` set an Authorization header
* Fixed `claude -w <name>` failing with "already exists" after a previous session's worktree cleanup left a stale directory
* Fixed subagents not inheriting MCP tools from dynamically-injected servers
* Fixed sub-agents running in isolated worktrees being denied Read/Edit access to files inside their own worktree
* Fixed sandboxed Bash commands failing with `mktemp: No such file or directory` after a fresh boot
* Fixed `claude mcp serve` tool calls failing with "Tool execution failed" in MCP clients that validate `outputSchema`
* Fixed `RemoteTrigger` tool's `run` action sending an empty body and being rejected by the server
* Fixed several `/resume` picker issues: narrow default view hiding sessions from other projects, unreachable preview on Windows Terminal, incorrect cwd in worktrees, session-not-found errors not surfacing in stderr, terminal title not being set, and resume hint overlapping the prompt input
* Fixed Grep tool ENOENT when the embedded ripgrep binary path becomes stale (VS Code extension auto-update, macOS App Translocation); now falls back to system `rg` and self-heals mid-session
* Fixed `/btw` writing a copy of the entire conversation to disk on every use
* Fixed `/context` Free space and Messages breakdown disagreeing with the header percentage
* Fixed several plugin issues: slash commands resolving to the wrong plugin with duplicate `name:` frontmatter, `/plugin update` failing with `ENAMETOOLONG`, Discover showing already-installed plugins, directory-source plugins loading from a stale version cache, and skills not honoring `context: fork` and `agent` frontmatter fields
* Fixed the `/mcp` menu offering OAuth-specific actions for MCP servers configured with `headersHelper`; Reconnect is now offered instead to re-invoke the helper script
* Fixed `ctrl+]`, `ctrl+\`, and `ctrl+^` keybindings not firing in terminals that send raw C0 control bytes (Terminal.app, default iTerm2, xterm)
* Fixed `/login` OAuth URL rendering with padding that prevented clean mouse selection
* Fixed rendering issues: flicker in non-fullscreen mode when content above the visible area changed, terminal scrollback being wiped during long sessions in non-fullscreen mode, and mouse-scroll escape sequences occasionally leaking into the prompt as text
* Fixed crash when `settings.json` env values are numbers instead of strings
* Fixed in-app settings writes (e.g. `/add-dir --remember`, `/config`) not refreshing the in-memory snapshot, preventing removed directories from being revoked mid-session
* Fixed custom keybindings (`~/.claude/keybindings.json`) not loading on Bedrock, Vertex, and other third-party providers
* Fixed `claude --continue -p` not correctly continuing sessions created by `-p` or the SDK
* Fixed several Remote Control issues: worktrees removed on session crash, connection failures not persisting in the transcript, spurious "Disconnected" indicator in brief mode for local sessions, and `/remote-control` failing over SSH when only `CLAUDE_CODE_ORGANIZATION_UUID` is set
* Fixed `/insights` sometimes omitting the report file link from its response
* \[VSCode] Fixed the file attachment below the chat input not clearing when the last editor tab is closed

### 2.1.98 (April 9, 2026)

* Added interactive Google Vertex AI setup wizard accessible from the login screen when selecting "3rd-party platform", guiding you through GCP authentication, project and region configuration, credential verification, and model pinning
* Added `CLAUDE_CODE_PERFORCE_MODE` env var: when set, Edit/Write/NotebookEdit fail on read-only files with a `p4 edit` hint instead of silently overwriting them
* Added Monitor tool for streaming events from background scripts
* Added subprocess sandboxing with PID namespace isolation on Linux when `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` is set, and `CLAUDE_CODE_SCRIPT_CAPS` env var to limit per-session script invocations
* Added `--exclude-dynamic-system-prompt-sections` flag to print mode for improved cross-user prompt caching
* Added `workspace.git_worktree` to the status line JSON input, set whenever the current directory is inside a linked git worktree
* Added W3C `TRACEPARENT` env var to Bash tool subprocesses when OTEL tracing is enabled, so child-process spans correctly parent to Claude Code's trace tree
* LSP: Claude Code now identifies itself to language servers via `clientInfo` in the initialize request
* Fixed a Bash tool permission bypass where a backslash-escaped flag could be auto-allowed as read-only and lead to arbitrary code execution
* Fixed compound Bash commands bypassing forced permission prompts for safety checks and explicit ask rules in auto and bypass-permissions modes
* Fixed read-only commands with env-var prefixes not prompting unless the var is known-safe (`LANG`, `TZ`, `NO_COLOR`, etc.)
* Fixed redirects to `/dev/tcp/...` or `/dev/udp/...` not prompting instead of auto-allowing
* Fixed stalled streaming responses timing out instead of falling back to non-streaming mode
* Fixed 429 retries burning all attempts in \~13s when the server returns a small `Retry-After` — exponential backoff now applies as a minimum
* Fixed MCP OAuth `oauth.authServerMetadataUrl` config override not being honored on token refresh after restart, affecting ADFS and similar IdPs
* Fixed capital letters being dropped to lowercase on xterm and VS Code integrated terminal when the kitty keyboard protocol is active
* Fixed macOS text replacements deleting the trigger word instead of inserting the substitution
* Fixed `--dangerously-skip-permissions` being silently downgraded to accept-edits mode after approving a write to a protected path via Bash
* Fixed managed-settings allow rules remaining active after an admin removed them, until process restart
* Fixed `permissions.additionalDirectories` changes not applying mid-session — removed directories lose access immediately and added ones work without restart
* Fixed removing a directory from `additionalDirectories` revoking access to the same directory passed via `--add-dir`
* Fixed `Bash(cmd:*)` and `Bash(git commit *)` wildcard permission rules failing to match commands with extra spaces or tabs
* Fixed `Bash(...)` deny rules being downgraded to a prompt for piped commands that mix `cd` with other segments
* Fixed false Bash permission prompts for `cut -d /`, `paste -d /`, `column -s /`, `awk '{print $1}' file`, and filenames containing `%`
* Fixed permission rules with names matching JavaScript prototype properties (e.g. `toString`) causing `settings.json` to be silently ignored
* Fixed agent team members not inheriting the leader's permission mode when using `--dangerously-skip-permissions`
* Fixed a crash in fullscreen mode when hovering over MCP tool results
* Fixed copying wrapped URLs in fullscreen mode inserting spaces at line breaks
* Fixed file-edit diffs disappearing from the UI on `--resume` when the edited file was larger than 10KB
* Fixed several `/resume` picker issues: `--resume <name>` opening uneditable, filter reload wiping search state, empty list swallowing arrow keys, cross-project staleness, and transient task-status text replacing conversation summaries
* Fixed `/export` not honoring absolute paths and `~`, and silently rewriting user-supplied extensions to `.txt`
* Fixed `/effort max` being denied for unknown or future model IDs
* Fixed slash command picker breaking when a plugin's frontmatter `name` is a YAML boolean keyword
* Fixed rate-limit upsell text being hidden after message remounts
* Fixed MCP tools with `_meta["anthropic/maxResultSizeChars"]` not bypassing the token-based persist layer
* Fixed voice mode leaking dozens of space characters into the input when re-holding the push-to-talk key while the previous transcript is still processing
* Fixed `DISABLE_AUTOUPDATER` not fully suppressing the npm registry version check and symlink modification on npm-based installs
* Fixed a memory leak where Remote Control permission handler entries were retained for the lifetime of the session
* Fixed background subagents that fail with an error not reporting partial progress to the parent agent
* Fixed prompt-type Stop/SubagentStop hooks failing on long sessions, and hook evaluator API errors showing "JSON validation failed" instead of the real message
* Fixed feedback survey rendering when dismissed
* Fixed Bash `grep -f FILE` / `rg -f FILE` not prompting when reading a pattern file outside the working directory
* Fixed stale subagent worktree cleanup removing worktrees that contain untracked files
* Fixed `sandbox.network.allowMachLookup` not taking effect on macOS
* Improved `/resume` filter hint labels and added project/worktree/branch names in the filter indicator
* Improved footer indicators (Focus, notifications) to stay on the mode-indicator row instead of wrapping at narrow terminal widths
* Improved `/agents` with a tabbed layout: a Running tab shows live subagents, and the Library tab adds Run agent and View running instance actions
* Improved `/reload-plugins` to pick up plugin-provided skills without requiring a restart
* Improved Accept Edits mode to auto-approve filesystem commands prefixed with safe env vars or process wrappers
* Improved Vim mode: `j`/`k` in NORMAL mode now navigate history and select the footer pill at the input boundary
* Improved hook errors in the transcript to include the first line of stderr for self-diagnosis without `--debug`
* Improved OTEL tracing: interaction spans now correctly wrap full turns under concurrent SDK calls, and headless turns end spans per-turn
* Improved transcript entries to carry final token usage instead of streaming placeholders
* Updated the `/claude-api` skill to cover Managed Agents alongside Claude API
* \[VSCode] Fixed false-positive "requires git-bash" error on Windows when `CLAUDE_CODE_GIT_BASH_PATH` is set or Git is installed at a default location
* Fixed `CLAUDE_CODE_MAX_CONTEXT_TOKENS` to honor `DISABLE_COMPACT` when it is set.
* Dropped `/compact` hints when `DISABLE_COMPACT` is set.

### 2.1.97 (April 8, 2026)

* Added focus view toggle (`Ctrl+O`) in `NO_FLICKER` mode showing prompt, one-line tool summary with edit diffstats, and final response
* Added `refreshInterval` status line setting to re-run the status line command every N seconds
* Added `workspace.git_worktree` to the status line JSON input, set when the current directory is inside a linked git worktree
* Added `● N running` indicator in `/agents` next to agent types with live subagent instances
* Added syntax highlighting for Cedar policy files (`.cedar`, `.cedarpolicy`)
* Fixed `--dangerously-skip-permissions` being silently downgraded to accept-edits mode after approving a write to a protected path
* Fixed and hardened Bash tool permissions, tightening checks around env-var prefixes and network redirects, and reducing false prompts on common commands
* Fixed permission rules with names matching JavaScript prototype properties (e.g. `toString`) causing `settings.json` to be silently ignored
* Fixed managed-settings allow rules remaining active after an admin removed them until process restart
* Fixed `permissions.additionalDirectories` changes in settings not applying mid-session
* Fixed removing a directory from `settings.permissions.additionalDirectories` revoking access to the same directory passed via `--add-dir`
* Fixed MCP HTTP/SSE connections accumulating \~50 MB/hr of unreleased buffers when servers reconnect
* Fixed MCP OAuth `oauth.authServerMetadataUrl` not being honored on token refresh after restart, fixing ADFS and similar IdPs
* Fixed 429 retries burning all attempts in \~13 seconds when the server returns a small `Retry-After` — exponential backoff now applies as a minimum
* Fixed rate-limit upgrade options disappearing after context compaction
* Fixed several `/resume` picker issues: `--resume <name>` opening uneditable, Ctrl+A reload wiping search, empty list swallowing navigation, task-status text replacing conversation summary, and cross-project staleness
* Fixed file-edit diffs disappearing on `--resume` when the edited file was larger than 10KB
* Fixed `--resume` cache misses and lost mid-turn input from attachment messages not being saved to the transcript
* Fixed messages typed while Claude is working not being persisted to the transcript
* Fixed prompt-type `Stop`/`SubagentStop` hooks failing on long sessions, and hook evaluator API errors displaying "JSON validation failed" instead of the actual message
* Fixed subagents with worktree isolation or `cwd:` override leaking their working directory back to the parent session's Bash tool
* Fixed compaction writing duplicate multi-MB subagent transcript files on prompt-too-long retries
* Fixed `claude plugin update` reporting "already at the latest version" for git-based marketplace plugins when the remote had newer commits
* Fixed slash command picker breaking when a plugin's frontmatter `name` is a YAML boolean keyword
* Fixed copying wrapped URLs in `NO_FLICKER` mode inserting spaces at line breaks
* Fixed scroll rendering artifacts in `NO_FLICKER` mode when running inside zellij
* Fixed a crash in `NO_FLICKER` mode when hovering over MCP tool results
* Fixed a `NO_FLICKER` mode memory leak where API retries left stale streaming state
* Fixed slow mouse-wheel scrolling in `NO_FLICKER` mode on Windows Terminal
* Fixed custom status line not displaying in `NO_FLICKER` mode on terminals shorter than 24 rows
* Fixed Shift+Enter and Alt/Cmd+arrow shortcuts not working in Warp with `NO_FLICKER` mode
* Fixed Korean/Japanese/Unicode text becoming garbled when copied in no-flicker mode on Windows
* Fixed Bedrock SigV4 authentication failing when `AWS_BEARER_TOKEN_BEDROCK` or `ANTHROPIC_BEDROCK_BASE_URL` are set to empty strings (as GitHub Actions does for unset inputs)
* Improved Accept Edits mode to auto-approve filesystem commands prefixed with safe env vars or process wrappers (e.g. `LANG=C rm foo`, `timeout 5 mkdir out`)
* Improved auto mode and bypass-permissions mode to auto-approve sandbox network access prompts
* Improved sandbox: `sandbox.network.allowMachLookup` now takes effect on macOS
* Improved image handling: pasted and attached images are now compressed to the same token budget as images read via the Read tool
* Improved slash command and `@`-mention completion to trigger after CJK sentence punctuation, so Japanese/Chinese input no longer requires a space before `/` or `@`
* Improved Bridge sessions to show the local git repo, branch, and working directory on the claude.ai session card
* Improved footer layout: indicators (Focus, notifications) now stay on the mode-indicator row instead of wrapping below
* Improved context-low warning to show as a transient footer notification instead of a persistent row
* Improved markdown blockquotes to show a continuous left bar across wrapped lines
* Improved session transcript size by skipping empty hook entries and capping stored pre-edit file copies
* Improved transcript accuracy: per-block entries now carry the final token usage instead of the streaming placeholder
* Improved Bash tool OTEL tracing: subprocesses now inherit a W3C `TRACEPARENT` env var when tracing is enabled
* Updated `/claude-api` skill to cover Managed Agents alongside the Claude API

### 2.1.96 (April 8, 2026)

* Fixed Bedrock requests failing with `403 "Authorization header is missing"` when using `AWS_BEARER_TOKEN_BEDROCK` or `CLAUDE_CODE_SKIP_BEDROCK_AUTH` (regression in 2.1.94)

### 2.1.94 (April 7, 2026)

* Added support for Amazon Bedrock powered by Mantle, set `CLAUDE_CODE_USE_MANTLE=1`
* Changed default effort level from medium to high for API-key, Bedrock/Vertex/Foundry, Team, and Enterprise users (control this with `/effort`)
* Added compact `Slacked #channel` header with a clickable channel link for Slack MCP send-message tool calls
* Added `keep-coding-instructions` frontmatter field support for plugin output styles
* Added `hookSpecificOutput.sessionTitle` to `UserPromptSubmit` hooks for setting the session title
* Plugin skills declared via `"skills": ["./"]` now use the skill's frontmatter `name` for the invocation name instead of the directory basename, giving a stable name across install methods
* Fixed agents appearing stuck after a 429 rate-limit response with a long Retry-After header — the error now surfaces immediately instead of silently waiting
* Fixed Console login on macOS silently failing with "Not logged in" when the login keychain is locked or its password is out of sync — the error is now surfaced and `claude doctor` diagnoses the fix
* Fixed plugin skill hooks defined in YAML frontmatter being silently ignored
* Fixed plugin hooks failing with "No such file or directory" when `CLAUDE_PLUGIN_ROOT` was not set
* Fixed `${CLAUDE_PLUGIN_ROOT}` resolving to the marketplace source directory instead of the installed cache for local-marketplace plugins on startup
* Fixed scrollback showing the same diff repeated and blank pages in long-running sessions
* Fixed multiline user prompts in the transcript indenting wrapped lines under the `❯` caret instead of under the text
* Fixed Shift+Space inserting the literal word "space" instead of a space character in search inputs
* Fixed hyperlinks opening two browser tabs when clicked inside tmux running in an xterm.js-based terminal (VS Code, Hyper, Tabby)
* Fixed an alt-screen rendering bug where content height changes mid-scroll could leave compounding ghost lines
* Fixed `FORCE_HYPERLINK` environment variable being ignored when set via `settings.json` `env`
* Fixed native terminal cursor not tracking the selected tab in dialogs, so screen readers and magnifiers can follow tab navigation
* Fixed Bedrock invocation of Sonnet 3.5 v2 by using the `us.` inference profile ID
* Fixed SDK/print mode not preserving the partial assistant response in conversation history when interrupted mid-stream
* Improved `--resume` to resume sessions from other worktrees of the same repo directly instead of printing a `cd` command
* Fixed CJK and other multibyte text being corrupted with U+FFFD in stream-json input/output when chunk boundaries split a UTF-8 sequence
* \[VSCode] Reduced cold-open subprocess work on starting a session
* \[VSCode] Fixed dropdown menus selecting the wrong item when the mouse was over the list while typing or using arrow keys
* \[VSCode] Added a warning banner when `settings.json` files fail to parse, so users know their permission rules are not being applied

### 2.1.92 (April 4, 2026)

* Added `forceRemoteSettingsRefresh` policy setting: when set, the CLI blocks startup until remote managed settings are freshly fetched, and exits if the fetch fails (fail-closed)
* Added interactive Bedrock setup wizard accessible from the login screen when selecting "3rd-party platform" — guides you through AWS authentication, region configuration, credential verification, and model pinning
* Added per-model and cache-hit breakdown to `/cost` for subscription users
* `/release-notes` is now an interactive version picker
* Remote Control session names now use your hostname as the default prefix (e.g. `myhost-graceful-unicorn`), overridable with `--remote-control-session-name-prefix`
* Pro users now see a footer hint when returning to a session after the prompt cache has expired, showing roughly how many tokens the next turn will send uncached
* Fixed subagent spawning permanently failing with "Could not determine pane count" after tmux windows are killed or renumbered during a long-running session
* Fixed prompt-type Stop hooks incorrectly failing when the small fast model returns `ok:false`, and restored `preventContinuation:true` semantics for non-Stop prompt-type hooks
* Fixed tool input validation failures when streaming emits array/object fields as JSON-encoded strings
* Fixed an API 400 error that could occur when extended thinking produced a whitespace-only text block alongside real content
* Fixed accidental feedback survey submissions from auto-pilot keypresses and consecutive-prompt digit collisions
* Fixed misleading "esc to interrupt" hint appearing alongside "esc to clear" when a text selection exists in fullscreen mode during processing
* Fixed Homebrew install update prompts to use the cask's release channel (`claude-code` → stable, `claude-code@latest` → latest)
* Fixed `ctrl+e` jumping to the end of the next line when already at end of line in multiline prompts
* Fixed an issue where the same message could appear at two positions when scrolling up in fullscreen mode (iTerm2, Ghostty, and other terminals with DEC 2026 support)
* Fixed idle-return "/clear to save X tokens" hint showing cumulative session tokens instead of current context size
* Fixed plugin MCP servers stuck "connecting" on session start when they duplicate a claude.ai connector that is unauthenticated
* Improved Write tool diff computation speed for large files (60% faster on files with tabs/`&`/`$`)
* Removed `/tag` command
* Removed `/vim` command (toggle vim mode via `/config` → Editor mode)
* Linux sandbox now ships the `apply-seccomp` helper in both npm and native builds, restoring unix-socket blocking for sandboxed commands

### 2.1.91 (April 2, 2026)

* Added MCP tool result persistence override via `_meta["anthropic/maxResultSizeChars"]` annotation (up to 500K), allowing larger results like DB schemas to pass through without truncation
* Added `disableSkillShellExecution` setting to disable inline shell execution in skills, custom slash commands, and plugin commands
* Added support for multi-line prompts in `claude-cli://open?q=` deep links (encoded newlines `%0A` no longer rejected)
* Plugins can now ship executables under `bin/` and invoke them as bare commands from the Bash tool
* Fixed transcript chain breaks on `--resume` that could lose conversation history when async transcript writes fail silently
* Fixed `cmd+delete` not deleting to start of line on iTerm2, kitty, WezTerm, Ghostty, and Windows Terminal
* Fixed plan mode in remote sessions losing track of the plan file after a container restart, which caused permission prompts on plan edits and an empty plan-approval modal
* Fixed JSON schema validation for `permissions.defaultMode: "auto"` in settings.json
* Fixed Windows version cleanup not protecting the active version's rollback copy
* `/feedback` now explains why it's unavailable instead of disappearing from the slash menu
* Improved `/claude-api` skill guidance for agent design patterns including tool surface decisions, context management, and caching strategy
* Improved performance: faster `stripAnsi` on Bun by routing through `Bun.stripANSI`
* Edit tool now uses shorter `old_string` anchors, reducing output tokens

### 2.1.90 (April 1, 2026)

* Added `/powerup` — interactive lessons teaching Claude Code features with animated demos
* Added `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE` env var to keep the existing marketplace cache when `git pull` fails, useful in offline environments
* Added `.husky` to protected directories (acceptEdits mode)
* Fixed an infinite loop where the rate-limit options dialog would repeatedly auto-open after hitting your usage limit, eventually crashing the session
* Fixed `--resume` causing a full prompt-cache miss on the first request for users with deferred tools, MCP servers, or custom agents (regression since v2.1.69)
* Fixed `Edit`/`Write` failing with "File content has changed" when a PostToolUse format-on-save hook rewrites the file between consecutive edits
* Fixed `PreToolUse` hooks that emit JSON to stdout and exit with code 2 not correctly blocking the tool call
* Fixed collapsed search/read summary badge appearing multiple times in fullscreen scrollback when a CLAUDE.md file auto-loads during a tool call
* Fixed auto mode not respecting explicit user boundaries ("don't push", "wait for X before Y") even when the action would otherwise be allowed
* Fixed click-to-expand hover text being nearly invisible on light terminal themes
* Fixed UI crash when malformed tool input reached the permission dialog
* Fixed headers disappearing when scrolling `/model`, `/config`, and other selection screens
* Hardened PowerShell tool permission checks: fixed trailing `&` background job bypass, `-ErrorAction Break` debugger hang, archive-extraction TOCTOU, and parse-fail fallback deny-rule degradation
* Improved performance: eliminated per-turn JSON.stringify of MCP tool schemas on cache-key lookup
* Improved performance: SSE transport now handles large streamed frames in linear time (was quadratic)
* Improved performance: SDK sessions with long conversations no longer slow down quadratically on transcript writes
* Improved `/resume` all-projects view to load project sessions in parallel, improving load times for users with many projects
* Changed `--resume` picker to no longer show sessions created by `claude -p` or SDK invocations
* Removed `Get-DnsClientCache` and `ipconfig /displaydns` from auto-allow (DNS cache privacy)

### 2.1.89 (April 1, 2026)

* Added `"defer"` permission decision to `PreToolUse` hooks — headless sessions can pause at a tool call and resume with `-p --resume` to have the hook re-evaluate
* Added `CLAUDE_CODE_NO_FLICKER=1` environment variable to opt into flicker-free alt-screen rendering with virtualized scrollback
* Added `PermissionDenied` hook that fires after auto mode classifier denials — return `{retry: true}` to tell the model it can retry
* Added named subagents to `@` mention typeahead suggestions
* Added `MCP_CONNECTION_NONBLOCKING=true` for `-p` mode to skip the MCP connection wait entirely, and bounded `--mcp-config` server connections at 5s instead of blocking on the slowest server
* Auto mode: denied commands now show a notification and appear in `/permissions` → Recent tab where you can retry with `r`
* Fixed `Edit(//path/**)` and `Read(//path/**)` allow rules to check the resolved symlink target, not just the requested path
* Fixed voice push-to-talk not activating for some modifier-combo bindings, and voice mode on Windows failing with "WebSocket upgrade rejected with HTTP 101"
* Fixed Edit/Write tools doubling CRLF on Windows and stripping Markdown hard line breaks (two trailing spaces)
* Fixed `StructuredOutput` schema cache bug causing \~50% failure rate when using multiple schemas
* Fixed memory leak where large JSON inputs were retained as LRU cache keys in long-running sessions
* Fixed a crash when removing a message from very large session files (over 50MB)
* Fixed LSP server zombie state after crash — server now restarts on next request instead of failing until session restart
* Fixed prompt history entries containing CJK or emoji being silently dropped when they fall on a 4KB boundary in `~/.claude/history.jsonl`
* Fixed `/stats` undercounting tokens by excluding subagent usage, and losing historical data beyond 30 days when the stats cache format changes
* Fixed `-p --resume` hangs when the deferred tool input exceeds 64KB or no deferred marker exists, and `-p --continue` not resuming deferred tools
* Fixed `claude-cli://` deep links not opening on macOS
* Fixed MCP tool errors truncating to only the first content block when the server returns multi-element error content
* Fixed skill reminders and other system context being dropped when sending messages with images via the SDK
* Fixed PreToolUse/PostToolUse hooks to receive `file_path` as an absolute path for Write/Edit/Read tools, matching the documented behavior
* Fixed autocompact thrash loop — now detects when context refills to the limit immediately after compacting three times in a row and stops with an actionable error instead of burning API calls
* Fixed prompt cache misses in long sessions caused by tool schema bytes changing mid-session
* Fixed nested CLAUDE.md files being re-injected dozens of times in long sessions that read many files
* Fixed `--resume` crash when transcript contains a tool result from an older CLI version or interrupted write
* Fixed misleading "Rate limit reached" message when the API returned an entitlement error — now shows the actual error with actionable hints
* Fixed hooks `if` condition filtering not matching compound commands (`ls && git push`) or commands with env-var prefixes (`FOO=bar git push`)
* Fixed collapsed search/read group badges duplicating in terminal scrollback during heavy parallel tool use
* Fixed notification `invalidates` not clearing the currently-displayed notification immediately
* Fixed prompt briefly disappearing after submit when background messages arrived during processing
* Fixed Devanagari and other combining-mark text being truncated in assistant output
* Fixed rendering artifacts on main-screen terminals after layout shifts
* Fixed voice mode failing to request microphone permission on macOS Apple Silicon
* Fixed Shift+Enter submitting instead of inserting a newline on Windows Terminal Preview 1.25
* Fixed periodic UI jitter d
