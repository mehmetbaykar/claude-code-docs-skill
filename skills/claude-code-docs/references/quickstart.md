---
title: "Quickstart"
source: https://code.claude.com/docs/en/quickstart
path: /docs/en/quickstart
---

# Quickstart

> Welcome to Claude Code!

This quickstart guide will have you using AI-powered coding assistance in a few minutes. By the end, you'll understand how to use Claude Code for common development tasks.

## Before you begin

Make sure you have:

* A terminal or command prompt open
* If you've never used the terminal before, check out the [terminal guide](https://code.claude.com/docs/en/terminal-guide)
* A code project to work with
* A [Claude subscription](https://claude.com/pricing?utm_source=claude_code\&utm_medium=docs\&utm_content=quickstart_prereq) (Pro, Max, Team, or Enterprise), [Claude Console](https://platform.claude.com/) account, or access through a [supported cloud provider](https://code.claude.com/docs/en/third-party-integrations)

This guide covers the terminal CLI. Claude Code is also available on the [web](https://claude.ai/code), as a [desktop app](https://code.claude.com/docs/en/desktop), in [VS Code](https://code.claude.com/docs/en/vs-code) and [JetBrains IDEs](https://code.claude.com/docs/en/jetbrains), in [Slack](https://code.claude.com/docs/en/slack), and in CI/CD with [GitHub Actions](https://code.claude.com/docs/en/github-actions) and [GitLab](https://code.claude.com/docs/en/gitlab-ci-cd). See [all interfaces](https://code.claude.com/docs/en/overview#use-claude-code-everywhere).

## Step 1: Install Claude Code

To install Claude Code, use one of the following methods:


**Native Install (Recommended)**

    **macOS, Linux, WSL:**
```bash
    curl -fsSL https://claude.ai/install.sh | bash
```

    **Windows PowerShell:**
```powershell
    irm https://claude.ai/install.ps1 | iex
```

    **Windows CMD:**
```batch
    curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

If you see `The token '&&' is not a valid statement separator`, you're in PowerShell, not CMD. If you see `'irm' is not recognized as an internal or external command`, you're in CMD, not PowerShell. Your prompt shows `PS C:\` when you're in PowerShell and `C:\` without the `PS` when you're in CMD.

If the install command fails with `syntax error near unexpected token '<'`, a `403`, or another curl error, see [Troubleshoot installation](https://code.claude.com/docs/en/troubleshoot-install#find-your-error) to match the error to a fix and for alternative install methods.

[Git for Windows](https://git-scm.com/downloads/win) is recommended on native Windows so Claude Code can use the Bash tool. If Git for Windows is not installed, Claude Code uses PowerShell as the shell tool instead. WSL setups do not need Git for Windows.


Native installations automatically update in the background to keep you on the latest version.




**Homebrew**
```bash
    brew install --cask claude-code
```

Homebrew offers two casks. `claude-code` tracks the stable release channel, which is typically about a week behind and skips releases with major regressions. `claude-code@latest` tracks the latest channel and receives new versions as soon as they ship.


Homebrew installations do not auto-update. Run `brew upgrade claude-code` or `brew upgrade claude-code@latest`, depending on which cask you installed, to get the latest features and security fixes.




**WinGet**
```powershell
    winget install Anthropic.ClaudeCode
```


WinGet installations do not auto-update. Run `winget upgrade Anthropic.ClaudeCode` periodically to get the latest features and security fixes.



You can also install with [apt, dnf, or apk](https://code.claude.com/docs/en/setup#install-with-linux-package-managers) on Debian, Fedora, RHEL, and Alpine.

To confirm the installation worked, run:
```bash
claude --version
```

The command prints a version number followed by `(Claude Code)`.

## Step 2: Log in to your account

Claude Code requires an account to use. Start an interactive session with the `claude` command and you'll be prompted to log in on first use:
```bash
claude
```

For Claude subscription or Console accounts, follow the prompts to complete authentication in your browser. If you've set the `ANTHROPIC_API_KEY` environment variable, Claude Code skips the login prompt and asks you to approve the key instead. To switch accounts later or re-authenticate, type `/login` inside the running session:
```text wrap
/login
```

You can log in using any of these account types:

* [Claude Pro, Max, Team, or Enterprise](https://claude.com/pricing?utm_source=claude_code\&utm_medium=docs\&utm_content=quickstart_login) (recommended)
* [Claude Console](https://platform.claude.com/) (API access with pre-paid credits). On first login, a "Claude Code" workspace is automatically created in the Console for centralized cost tracking.
* [Amazon Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry](https://code.claude.com/docs/en/third-party-integrations) (enterprise cloud providers)
* A self-hosted [Claude apps gateway](https://code.claude.com/docs/en/claude-apps-gateway), if your organization runs one: your admin pre-configures the gateway URL, and `/login` opens directly on the **Cloud gateway** screen for you to sign in with corporate SSO

Once logged in, your credentials are stored and you won't need to log in again. Learn more in [Credential Management](https://code.claude.com/docs/en/authentication#credential-management).

## Step 3: Start your first session

Open your terminal in any project directory and start Claude Code:
```bash
cd /path/to/your/project
claude
```

Replace `/path/to/your/project` with the path to the project you want to work on.

You'll see the Claude Code prompt with the version, current model, and working directory shown above it. Type `/help` for available commands or `/resume` to continue a previous conversation.

## Step 4: Ask your first question

Let's start with understanding your codebase. Try one of these commands:
```text wrap
what does this project do?
```

Claude will analyze your files and provide a summary. You can also ask more specific questions:
```text wrap
what technologies does this project use?
```
```text wrap
where is the main entry point?
```
```text wrap
explain the folder structure
```

You can also ask Claude about its own capabilities:
```text wrap
what can Claude Code do?
```
```text wrap
how do I create custom skills in Claude Code?
```
```text wrap
can Claude Code work with Docker?
```

Claude Code reads your project files as needed. You don't have to manually add context.

## Step 5: Make your first code change

Now let's make Claude Code do some actual coding. Try a simple task:
```text wrap
add a hello world function to the main file
```

Claude Code finds the appropriate file and shows you the change. In your first session after installing, it asks before each change. Select **Yes** to approve.

After your first session, auto mode is the [built-in starting permission mode](https://code.claude.com/docs/en/permission-modes#eliminate-prompts-with-auto-mode) for interactive terminal sessions on Pro, Max, and Team plans: a classifier reviews actions instead of you, and Claude edits most files and runs most commands without asking you. On other plans, Manual mode is the built-in starting permission mode.

Your settings or your organization can set a different starting permission mode. [Which permission mode a session starts in](https://code.claude.com/docs/en/permission-modes#which-mode-a-session-starts-in) lists what does. Press `Shift+Tab` at any time to switch the permission mode of the session you're in.

## Step 6: Use Git with Claude Code

Claude Code makes Git operations conversational:
```text wrap
what files have I changed?
```
```text wrap
commit my changes with a descriptive message
```

You can also prompt for more complex Git operations:
```text wrap
create a new branch called feature/quickstart
```
```text wrap
show me the last 5 commits
```
```text wrap
help me resolve merge conflicts
```

## Step 7: Fix a bug or add a feature

Claude is proficient at debugging and feature implementation.

Describe what you want in natural language:
```text wrap
add input validation to the user registration form
```

Or fix existing issues:
```text wrap
there's a bug where users can submit empty forms - fix it
```

Claude Code will:

* Locate the relevant code
* Understand the context
* Implement a solution
* Run tests if available

## Step 8: Test out other common workflows

There are a number of ways to work with Claude:

**Refactor code**
```text wrap
refactor the authentication module to use async/await instead of callbacks
```

**Write tests**
```text wrap
write unit tests for the calculator functions
```

**Update documentation**
```text wrap
update the README with installation instructions
```

**Code review**
```text wrap
review my changes and suggest improvements
```

Talk to Claude like you would a helpful colleague. Describe what you want to achieve, and it will help you get there.

## Essential commands

Here are the most important commands for daily use. Shell commands run from your terminal to start or resume Claude Code. Session commands run inside Claude Code after it starts.

**Shell commands**

| Command             | What it does                                           | Example                             |
| ------------------- | ------------------------------------------------------ | ----------------------------------- |
| `claude`            | Start interactive mode                                 | `claude`                            |
| `claude "task"`     | Start interactive mode with an initial prompt          | `claude "fix the build error"`      |
| `claude -p "query"` | Run one-off query, then exit                           | `claude -p "explain this function"` |
| `claude -c`         | Continue most recent conversation in current directory | `claude -c`                         |
| `claude -r`         | Resume a previous conversation                         | `claude -r`                         |

**Session commands**

| Command                 | What it does               | Example  |
| ----------------------- | -------------------------- | -------- |
| `/clear`                | Clear conversation history | `/clear` |
| `/help`                 | Show available commands    | `/help`  |
| `/exit` or Ctrl+D twice | Exit Claude Code           | `/exit`  |

See the [CLI reference](https://code.claude.com/docs/en/cli-reference) for the complete list of shell commands and the [commands reference](https://code.claude.com/docs/en/commands) for the complete list of session commands.

## Pro tips for beginners

For more, see [best practices](https://code.claude.com/docs/en/best-practices) and [common workflows](https://code.claude.com/docs/en/common-workflows).


**Be specific with your requests**

Instead of: "fix the bug"

Try: "fix the login bug where users see a blank screen after entering wrong credentials"



**Use step-by-step instructions**

Break complex tasks into steps:
```text wrap
    1. create a new database table for user profiles
    2. create an API endpoint to get and update user profiles
    3. build a webpage that allows users to see and edit their information
```



**Let Claude explore first**

Before making changes, let Claude understand your code:
```text wrap
    analyze the database schema
```
```text wrap
    build a dashboard showing products that are most frequently returned by our UK customers
```



**Save time with shortcuts**

* Type `/` to see the commands and skills available to you
* Use Tab for command completion
* Press ↑ for command history
* Press `Shift+Tab` to cycle permission modes


## What's next?

Now that you've learned the basics, explore more advanced features:


**How Claude Code works**

Understand the agentic loop, built-in tools, and how Claude Code interacts with your project



**Best practices**

Get better results with effective prompting and project setup



**Common workflows**

Step-by-step guides for common tasks



**Extend Claude Code**

Customize with CLAUDE.md, skills, hooks, MCP, and more


## Getting help

* **In Claude Code**: Type `/help` or ask "how do I..."
* **Documentation**: You're here! Browse other guides
* **Community**: Join our [Discord](https://www.anthropic.com/discord) for tips and support
