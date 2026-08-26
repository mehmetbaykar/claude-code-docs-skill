---
title: "Feature availability"
source: https://code.claude.com/docs/en/feature-availability
path: /docs/en/feature-availability
---

# Feature availability

> Compare which Claude Code features are available across Anthropic subscription plans, the Anthropic Console, Amazon Bedrock, Claude Platform on AWS, Google Cloud's Agent Platform, and Microsoft Foundry.

The Claude Code CLI and everything that runs locally work on every provider. For setup instructions per provider, see the [Enterprise deployment overview](https://code.claude.com/docs/en/third-party-integrations). To skip straight to what is missing on your provider, see the [summary by provider](#summary-by-provider) tabs.

In the tables below, ✓ means available, ✗ means not available, and "See note" links to a footnote for partial support. A qualifier after ✓ narrows availability to that subset, and "Admin-enabled" means the feature is off until an organization admin turns it on.

## Availability by model provider

How you authenticate determines which features Claude Code can reach. For a single list of what is missing on your provider, see the [summary by provider](#summary-by-provider) tabs. To find your column in the tables:

* **Claude subscription**: you sign in with a claude.ai account on the Pro, Max, Team, or Enterprise plan
* **Anthropic Console**: you authenticate with an Anthropic API key
* **Amazon Bedrock**: you use Claude models from the Amazon Bedrock model catalog and set `CLAUDE_CODE_USE_BEDROCK`. The [Mantle endpoint](https://code.claude.com/docs/en/amazon-bedrock#use-the-mantle-endpoint) (`CLAUDE_CODE_USE_MANTLE`) is covered by this column
* **Claude Platform on AWS**: you bought Claude through AWS Marketplace but call the Anthropic API, and set `CLAUDE_CODE_USE_ANTHROPIC_AWS`
* **Google Cloud's Agent Platform**: Google-operated; you set `CLAUDE_CODE_USE_VERTEX`
* **Microsoft Foundry**: Anthropic-operated; you set `CLAUDE_CODE_USE_FOUNDRY`

### Features available on every provider

These work on every provider:

* [CLI](https://code.claude.com/docs/en/quickstart) and [Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)
* [VS Code](https://code.claude.com/docs/en/vs-code) and [JetBrains](https://code.claude.com/docs/en/jetbrains) extensions
* [Subagents](https://code.claude.com/docs/en/sub-agents), [hooks](https://code.claude.com/docs/en/hooks-guide), [commands](https://code.claude.com/docs/en/commands), and [skills](https://code.claude.com/docs/en/skills)
* [CLAUDE.md memory](https://code.claude.com/docs/en/memory), [plugins](https://code.claude.com/docs/en/plugins), and [MCP servers](https://code.claude.com/docs/en/mcp)
* [Checkpoints](https://code.claude.com/docs/en/checkpointing), [sandboxing](https://code.claude.com/docs/en/sandboxing), and [Workflows](https://code.claude.com/docs/en/workflows)
* [OpenTelemetry metrics](https://code.claude.com/docs/en/monitoring-usage) and the [managed settings file](https://code.claude.com/docs/en/managed-settings#delivery-mechanisms)

Three of these have provider-specific differences:

* **MCP servers**: [connectors from claude.ai](https://code.claude.com/docs/en/mcp#use-mcp-servers-from-claude-ai) load only when your claude.ai subscription is the active authentication method. [Tool search](https://code.claude.com/docs/en/mcp#configure-tool-search) is off by default when `ANTHROPIC_BASE_URL` points to a non-first-party host, and isn't supported on Google Cloud's Agent Platform models earlier than the Claude 4.5 generation or on Microsoft Foundry [deployments hosted on Azure](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#hosting-options)
* **Subagents**: the built-in [Explore subagent](https://code.claude.com/docs/en/sub-agents#built-in-subagents) caps its inherited model at Opus on the Claude API, and inherits the main conversation's model directly on any other provider, including Claude Platform on AWS
* **[Commands](https://code.claude.com/docs/en/commands#all-commands)**: `/design-sync`, `/import` with its `claude import` subcommand form, and `/radio` are unavailable on Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, and Claude Platform on AWS, `/voice` requires a claude.ai account, and `/list-agents` and its alias `/peers` are available only in sessions where [cross-session messaging is enabled](https://code.claude.com/docs/en/cross-session-messaging#availability)

### Features that require a Claude subscription

These require signing in with a claude.ai account and are not reachable with an Anthropic Console API key or from a third-party provider:

* [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web), Claude Code on mobile, and [Claude Code in Slack](https://code.claude.com/docs/en/slack)
* [Claude Code Desktop](https://code.claude.com/docs/en/desktop)
* [Routines](https://code.claude.com/docs/en/routines) (`/schedule`)
* [Ultrareview](https://code.claude.com/docs/en/ultrareview)
* [Code Review](https://code.claude.com/docs/en/code-review): Team and Enterprise plans
* [Remote Control](https://code.claude.com/docs/en/remote-control)
* [Chrome extension](https://code.claude.com/docs/en/chrome)
* [Computer use](https://code.claude.com/docs/en/computer-use): Pro and Max plans
* [Artifacts](https://code.claude.com/docs/en/artifacts): Pro, Max, Team, and Enterprise plans
* [Voice dictation](https://code.claude.com/docs/en/voice-dictation)

Desktop is the partial exception: [gateway routing can be configured in the app or by an administrator](https://code.claude.com/docs/en/llm-gateway-connect#desktop-app), Enterprise deployments can route Desktop to Google Cloud's Agent Platform or a gateway provider via [managed settings](https://claude.com/docs/third-party/claude-desktop/configuration), and [Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview) runs the Code tab on Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, or a self-hosted LLM gateway. For per-plan availability of these features, see [Availability by subscription plan](#availability-by-subscription-plan).

### CLI capabilities that vary by provider

These features work in the local CLI but depend on a server-side capability that not every provider exposes.

| Feature | Claude subscription | Anthropic Console | Amazon Bedrock | Claude Platform on AWS | Google Cloud's Agent Platform | Microsoft Foundry |
| --- | --- | --- | --- | --- | --- | --- |
| [Web search](https://code.claude.com/docs/en/tools-reference#websearch-tool-behavior) | ✓ | ✓ | ✗ | ✓ | See note [1](#fn1) | ✓ ([deployments hosted on Anthropic](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#hosting-options)) |
| [Fast mode](https://code.claude.com/docs/en/fast-mode) | ✓ ([Owner-enabled](https://code.claude.com/docs/en/fast-mode#enable-fast-mode-for-your-organization) on Team and Enterprise) | ✓ (provisioned organizations) | ✗ | ✗ | ✗ | ✗ |
| [Auto mode](https://code.claude.com/docs/en/auto-mode-config) | ✓ | ✓ | See note [2](#fn2) | ✓ | See note [2](#fn2) | See note [2](#fn2) |
| [Advisor](https://code.claude.com/docs/en/advisor) | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| [Cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging) | ✓ [6](#fn6) | ✓ [6](#fn6) | ✗ | ✗ | ✗ | ✗ |
| [Channels](https://code.claude.com/docs/en/channels) | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| [`/loop` scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks) | ✓ | ✓ | See note [3](#fn3) | See note [3](#fn3) | See note [3](#fn3) | See note [3](#fn3) |
| [GitHub Actions](https://code.claude.com/docs/en/github-actions) | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| [GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd) | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |

### Admin and analytics

Organization-level controls and usage visibility.

| Feature | Claude subscription | Anthropic Console | Amazon Bedrock | Claude Platform on AWS | Google Cloud's Agent Platform | Microsoft Foundry |
| --- | --- | --- | --- | --- | --- | --- |
| [Analytics dashboard and API](https://code.claude.com/docs/en/analytics) | ✓ (dashboard: Team and Enterprise; API: Enterprise) | ✓ [5](#fn5) | ✗ | ✗ | ✗ | ✗ |
| [Server-managed settings](https://code.claude.com/docs/en/server-managed-settings) | ✓ (Team and Enterprise) | ✓ (Team and Enterprise) | ✗ | ✗ | ✗ | ✗ |
| [Zero Data Retention](https://code.claude.com/docs/en/zero-data-retention) | ✓ (qualified Enterprise accounts) | ✓ (qualified accounts) | See note [4](#fn4) | ✓ (qualified accounts) | See note [4](#fn4) | See note [4](#fn4) |

<sup>6</sup> Requires Claude Code v2.1.224 or later on macOS and Linux, including Linux inside WSL 2. On native Windows, requires Claude Code v2.1.234 or later. With API key authentication, same-machine messaging only. Claude can find your [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web) sessions and your sessions on other machines only from a session that is connected to [Remote Control](https://code.claude.com/docs/en/remote-control). Connecting needs a claude.ai sign-in and the other [Remote Control requirements](https://code.claude.com/docs/en/remote-control#requirements). See [Message sessions on other machines](https://code.claude.com/docs/en/cross-session-messaging#message-sessions-on-other-machines).

If you authenticate through an [LLM gateway](https://code.claude.com/docs/en/llm-gateway), feature availability matches the underlying provider the gateway forwards to. Some Anthropic-only features such as the [Advisor](https://code.claude.com/docs/en/advisor) work only if the gateway forwards requests intact to the Anthropic API.

### Summary by provider

Each tab lists what is unavailable or partially supported on that provider, with alternatives where one exists. Everything not listed works the same as on a Claude subscription, apart from the [provider-specific differences](#features-available-on-every-provider) noted above. On Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, and Claude Platform on AWS, error reporting and telemetry to Anthropic are off by default. See [default behaviors by API provider](https://code.claude.com/docs/en/data-usage#default-behaviors-by-api-provider) for what traffic still reaches Anthropic and how to opt out.


**Amazon Bedrock**

    **Not available:** all [features that require a Claude subscription](#features-that-require-a-claude-subscription), plus [web search](https://code.claude.com/docs/en/tools-reference#websearch-tool-behavior), [fast mode](https://code.claude.com/docs/en/fast-mode), [Advisor](https://code.claude.com/docs/en/advisor), [Channels](https://code.claude.com/docs/en/channels), [cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging), the [analytics dashboard](https://code.claude.com/docs/en/analytics), [server-managed settings](https://code.claude.com/docs/en/server-managed-settings), and the [`/design-sync`, `/import`, and `/radio` commands](https://code.claude.com/docs/en/commands#all-commands).

    **Partial support:**

* [Desktop](https://code.claude.com/docs/en/desktop): only via [Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview)
* [Auto mode](https://code.claude.com/docs/en/auto-mode-config): Sonnet 5, Opus 4.7 or later, and Fable 5 only
* [`/loop`](https://code.claude.com/docs/en/scheduled-tasks): explicit intervals only
* [Zero Data Retention](https://code.claude.com/docs/en/zero-data-retention): subject to your AWS agreement

    **Alternatives:** for scheduling, use [`/loop`](https://code.claude.com/docs/en/scheduled-tasks) with an explicit interval instead of `/schedule`. For cloud sessions, use [GitHub Actions](https://code.claude.com/docs/en/github-actions) or [GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd). For web lookups, use the [WebFetch tool](https://code.claude.com/docs/en/tools-reference#webfetch-tool-behavior) with a specific URL.



**Claude Platform on AWS**

    **Not available:** all [features that require a Claude subscription](#features-that-require-a-claude-subscription), plus [fast mode](https://code.claude.com/docs/en/fast-mode), [Advisor](https://code.claude.com/docs/en/advisor), [Channels](https://code.claude.com/docs/en/channels), [cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging), [GitHub Actions](https://code.claude.com/docs/en/github-actions), the [analytics dashboard](https://code.claude.com/docs/en/analytics), [server-managed settings](https://code.claude.com/docs/en/server-managed-settings), and the [`/design-sync`, `/import`, and `/radio` commands](https://code.claude.com/docs/en/commands#all-commands).

    **Available where Amazon Bedrock is not:** [web search](https://code.claude.com/docs/en/tools-reference#websearch-tool-behavior).

    **Partial support:**

* [`/loop`](https://code.claude.com/docs/en/scheduled-tasks): explicit intervals only

    **Alternatives:** for scheduling, use [`/loop`](https://code.claude.com/docs/en/scheduled-tasks) with an explicit interval instead of `/schedule`. For cloud sessions, use [GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd).



**Google Cloud's Agent Platform**

    **Not available:** all [features that require a Claude subscription](#features-that-require-a-claude-subscription), plus [fast mode](https://code.claude.com/docs/en/fast-mode), [Advisor](https://code.claude.com/docs/en/advisor), [Channels](https://code.claude.com/docs/en/channels), [cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging), the [analytics dashboard](https://code.claude.com/docs/en/analytics), [server-managed settings](https://code.claude.com/docs/en/server-managed-settings), and the [`/design-sync`, `/import`, and `/radio` commands](https://code.claude.com/docs/en/commands#all-commands).

    **Partial support:**

* [Desktop](https://code.claude.com/docs/en/desktop): via [managed settings](https://claude.com/docs/third-party/claude-desktop/configuration) or [Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview)
* [Web search](https://code.claude.com/docs/en/tools-reference#websearch-tool-behavior): Claude 4 models and later
* [Auto mode](https://code.claude.com/docs/en/auto-mode-config): Sonnet 5, Opus 4.7 or later, and Fable 5 only
* [`/loop`](https://code.claude.com/docs/en/scheduled-tasks): explicit intervals only
* [Zero Data Retention](https://code.claude.com/docs/en/zero-data-retention): subject to your Google Cloud agreement

    **Alternatives:** for scheduling, use [`/loop`](https://code.claude.com/docs/en/scheduled-tasks) with an explicit interval instead of `/schedule`. For cloud sessions, use [GitHub Actions](https://code.claude.com/docs/en/github-actions) or [GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd).



**Microsoft Foundry**

    **Not available:** all [features that require a Claude subscription](#features-that-require-a-claude-subscription), plus [fast mode](https://code.claude.com/docs/en/fast-mode), [Advisor](https://code.claude.com/docs/en/advisor), [Channels](https://code.claude.com/docs/en/channels), [cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging), [GitLab CI/CD](https://code.claude.com/docs/en/gitlab-ci-cd), the [analytics dashboard](https://code.claude.com/docs/en/analytics), [server-managed settings](https://code.claude.com/docs/en/server-managed-settings), and the [`/design-sync`, `/import`, and `/radio` commands](https://code.claude.com/docs/en/commands#all-commands).

    **Partial support:**

* [Desktop](https://code.claude.com/docs/en/desktop): only via [Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview)
* [Web search](https://code.claude.com/docs/en/tools-reference#websearch-tool-behavior): [deployments hosted on Anthropic](https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry#hosting-options) only
* [Auto mode](https://code.claude.com/docs/en/auto-mode-config): Sonnet 5, Opus 4.7 or later, and Fable 5 only
* [`/loop`](https://code.claude.com/docs/en/scheduled-tasks): explicit intervals only
* [Zero Data Retention](https://code.claude.com/docs/en/zero-data-retention): subject to your Azure agreement

    **Alternatives:** for scheduling, use [`/loop`](https://code.claude.com/docs/en/scheduled-tasks) with an explicit interval instead of `/schedule`. For cloud sessions, use [GitHub Actions](https://code.claude.com/docs/en/github-actions).



**Anthropic Console**

    **Not available:** all [features that require a Claude subscription](#features-that-require-a-claude-subscription).

Everything in [CLI capabilities that vary by provider](#cli-capabilities-that-vary-by-provider) is available, except that [fast mode](https://code.claude.com/docs/en/fast-mode) requires [provisioned access](https://code.claude.com/docs/en/fast-mode#enable-fast-mode-for-your-organization). [Server-managed settings](https://code.claude.com/docs/en/server-managed-settings) are also available when your API key belongs to a Team or Enterprise organization.


## Availability by subscription plan

If you authenticate through Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, or an Anthropic Console API key, this section does not apply to you. When you sign in with a claude.ai account, your plan determines which of the features below are available.

| Feature                                                                     | Pro | Max | Team          | Enterprise                        |
| :-------------------------------------------------------------------------- | :-- | :-- | :------------ | :-------------------------------- |
| [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)                        | ✓   | ✓   | ✓             | ✓ <sup>[7](#fn7)</sup> |
| [Routines](https://code.claude.com/docs/en/routines)                                                    | ✓   | ✓   | ✓             | ✓                                 |
| [Remote Control](https://code.claude.com/docs/en/remote-control)                                        | ✓   | ✓   | Admin-enabled | Admin-enabled                     |
| [Channels](https://code.claude.com/docs/en/channels)                                                    | ✓   | ✓   | Admin-enabled | Admin-enabled                     |
| [Computer use](https://code.claude.com/docs/en/computer-use)                                            | ✓   | ✓   | ✗             | ✗                                 |
| Dispatch ([Desktop](https://code.claude.com/docs/en/desktop#sessions-from-dispatch))                    | ✓   | ✓   | ✗             | ✗                                 |
| [Code Review](https://code.claude.com/docs/en/code-review)                                              | ✗   | ✗   | ✓             | ✓                                 |
| [Artifacts](https://code.claude.com/docs/en/artifacts)                                                  | ✓   | ✓   | ✓             | Admin-enabled                     |
| [Analytics dashboard and contribution metrics](https://code.claude.com/docs/en/analytics)               | ✗   | ✗   | ✓             | ✓                                 |
| [Enterprise Analytics API](https://code.claude.com/docs/en/analytics#access-data-programmatically)      | ✗   | ✗   | ✗             | ✓                                 |
| [Server-managed settings](https://code.claude.com/docs/en/server-managed-settings)                      | ✗   | ✗   | ✓             | ✓                                 |
| [SSO](https://support.claude.com/en/articles/9266767-what-is-the-team-plan) | ✗   | ✗   | ✓             | ✓                                 |
| SCIM                                                                        | ✗   | ✗   | ✗             | ✓                                 |
| [Compliance API](https://platform.claude.com/docs/en/api/compliance)        | ✗   | ✗   | ✗             | ✓                                 |
| [Zero Data Retention](https://code.claude.com/docs/en/zero-data-retention)                              | ✗   | ✗   | ✗             | ✓ <sup>[8](#fn8)</sup> |

<sup>8</sup> Not included in the standard Enterprise plan. Requires separate enablement by Anthropic for qualified accounts. See [Zero Data Retention](https://code.claude.com/docs/en/zero-data-retention).

For pricing and the full plan comparison, see [Team plans](https://support.claude.com/en/articles/9266767-what-is-the-team-plan) and [Enterprise plans](https://support.claude.com/en/articles/9797531-what-is-the-enterprise-plan).

## Model availability

For which Claude models and context-window sizes are available per provider and region, see [Model configuration](https://code.claude.com/docs/en/model-config) and the [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview). Vision, PDF input, and extended thinking are model capabilities rather than Claude Code features and work on every provider that offers the model. [Prompt caching](https://code.claude.com/docs/en/prompt-caching) works the same way on most providers; on Amazon Bedrock, support varies by model.

## Related resources

* [Enterprise deployment overview](https://code.claude.com/docs/en/third-party-integrations): compare authentication, billing, and regions across providers
* Provider setup guides: [Amazon Bedrock](https://code.claude.com/docs/en/amazon-bedrock), [Claude Platform on AWS](https://code.claude.com/docs/en/claude-platform-on-aws), [Google Cloud's Agent Platform](https://code.claude.com/docs/en/google-vertex-ai), [Microsoft Foundry](https://code.claude.com/docs/en/microsoft-foundry)
* [Platforms and integrations](https://code.claude.com/docs/en/platforms): where Claude Code runs, including the CLI, Desktop, IDE extensions, web, mobile, and CI/CD
