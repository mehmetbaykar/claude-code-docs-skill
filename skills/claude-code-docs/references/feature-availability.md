---
title: Feature availability
source: https://code.claude.com/docs/en/feature-availability
path: /docs/en/feature-availability
---

# Feature availability

> Compare which Claude Code features are available across Anthropic subscription plans, the Anthropic Console, Amazon Bedrock, Claude Platform on AWS, Google Cloud's Agent Platform, and Microsoft Foundry.

The Claude Code CLI and everything that runs locally work identically on every provider. For setup instructions per provider, see the [Enterprise deployment overview](/en/third-party-integrations). To skip straight to what is missing on your provider, see the [summary by provider](#summary-by-provider) tabs.

In the tables below, ✓ means available, ✗ means not available, and "See note" links to a footnote for partial support. A qualifier after ✓ narrows availability to that subset, and "Admin-enabled" means the feature is off until an organization admin turns it on.

## Availability by model provider

How you authenticate determines which features Claude Code can reach. For a single list of what is missing on your provider, see the [summary by provider](#summary-by-provider) tabs. To find your column in the tables:

* **Claude subscription**: you sign in with a claude.ai account on the Pro, Max, Team, or Enterprise plan
* **Anthropic Console**: you authenticate with an Anthropic API key
* **Amazon Bedrock**: you use Claude models from the Amazon Bedrock model catalog and set `CLAUDE_CODE_USE_BEDROCK`. The [Mantle endpoint](/en/amazon-bedrock#use-the-mantle-endpoint) (`CLAUDE_CODE_USE_MANTLE`) is covered by this column
* **Claude Platform on AWS**: you bought Claude through AWS Marketplace but call the Anthropic API, and set `CLAUDE_CODE_USE_ANTHROPIC_AWS`
* **Google Cloud's Agent Platform**: Google-operated; you set `CLAUDE_CODE_USE_VERTEX`
* **Microsoft Foundry**: Anthropic-operated on Azure; you set `CLAUDE_CODE_USE_FOUNDRY`

### Features available on every provider

These work identically on every provider:

* [CLI](/en/quickstart) and [Agent SDK](/en/agent-sdk/overview)
* [VS Code](/en/vs-code) and [JetBrains](/en/jetbrains) extensions
* [Subagents](/en/sub-agents), [hooks](/en/hooks-guide), [commands](/en/commands), and [skills](/en/skills)
* [CLAUDE.md memory](/en/memory), [plugins](/en/plugins), and [MCP servers](/en/mcp)
* [Checkpoints](/en/checkpointing), [sandboxing](/en/sandboxing), and [Workflows](/en/workflows)
* [OpenTelemetry metrics](/en/monitoring-usage) and the [managed settings file](/en/settings#settings-files)

### Features that require a Claude subscription

These require signing in with a claude.ai account and are not reachable with an Anthropic Console API key or from a third-party provider:

* [Claude Code on the web](/en/claude-code-on-the-web), Claude Code on mobile, and [Claude Code in Slack](/en/slack)
* [Claude Code Desktop](/en/desktop)
* [Routines](/en/routines) (`/schedule`)
* [Ultraplan](/en/ultraplan) and [Ultrareview](/en/ultrareview)
* [Code Review](/en/code-review): Team and Enterprise plans
* [Remote Control](/en/remote-control)
* [Chrome extension](/en/chrome)
* [Computer use](/en/computer-use): Pro and Max plans
* [Artifacts](/en/artifacts): Pro, Max, Team, and Enterprise plans
* [Voice dictation](/en/voice-dictation)

Desktop is the partial exception: Enterprise deployments can route Desktop to Google Cloud's Agent Platform or a gateway provider via [managed settings](https://support.claude.com/en/articles/12622667-enterprise-configuration), and [Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview) runs the Code tab on Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, or a self-hosted LLM gateway. For per-plan availability of these features, see [Availability by subscription plan](#availability-by-subscription-plan).

### CLI capabilities that vary by provider

These features work in the local CLI but depend on a server-side capability that not every provider exposes.

| Feature | Claude subscription | Anthropic Console | Amazon Bedrock | Claude Platform on AWS | Google Cloud's Agent Platform | Microsoft Foundry |
| --- | --- | --- | --- | --- | --- | --- |
| [Web search](/en/tools-reference#websearch-tool-behavior) | ✓ | ✓ | ✗ | ✓ | See note [1](#fn1) | ✓ |
| [Fast mode](/en/fast-mode) | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| [Auto mode](/en/auto-mode-config) | ✓ | ✓ | See note [2](#fn2) | ✓ | See note [2](#fn2) | See note [2](#fn2) |
| [Advisor](/en/advisor) | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| [Channels](/en/channels) | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| [`/loop` scheduled tasks](/en/scheduled-tasks) | ✓ | ✓ | See note [3](#fn3) | ✓ | See note [3](#fn3) | See note [3](#fn3) |
| [GitHub Actions](/en/github-actions) and [GitLab CI/CD](/en/gitlab-ci-cd) | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |

### Admin and analytics

Organization-level controls and usage visibility.

| Feature | Claude subscription | Anthropic Console | Amazon Bedrock | Claude Platform on AWS | Google Cloud's Agent Platform | Microsoft Foundry |
| --- | --- | --- | --- | --- | --- | --- |
| [Analytics dashboard and API](/en/analytics) | ✓ (dashboard: Team and Enterprise; API: Enterprise) | ✓ [5](#fn5) | ✗ | ✗ | ✗ | ✗ |
| [Server-managed settings](/en/server-managed-settings) | ✓ (Team and Enterprise) | ✓ (Team and Enterprise) | ✗ | ✗ | ✗ | ✗ |
| [Zero Data Retention](/en/zero-data-retention) | ✓ (qualified Enterprise accounts) | ✓ (qualified accounts) | See note [4](#fn4) | ✓ (qualified accounts) | See note [4](#fn4) | See note [4](#fn4) |

<sup>5</sup> Dashboard and API only. [Contribution metrics](/en/analytics#enable-contribution-metrics) requires a claude.ai Team or Enterprise organization.

If you authenticate through an [LLM gateway](/en/llm-gateway), feature availability matches the underlying provider the gateway forwards to. Some Anthropic-only features such as the [Advisor](/en/advisor) work only if the gateway forwards requests intact to the Anthropic API.

### Summary by provider

Each tab lists what is unavailable or partially supported on that provider, with alternatives where one exists. Everything not listed works the same as on a Claude subscription. On Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, and Claude Platform on AWS, error reporting and telemetry to Anthropic are off by default. See [default behaviors by API provider](/en/data-usage#default-behaviors-by-api-provider) for what traffic still reaches Anthropic and how to opt out.


**Amazon Bedrock**

    **Not available:** all [features that require a Claude subscription](#features-that-require-a-claude-subscription), plus [web search](/en/tools-reference#websearch-tool-behavior), [fast mode](/en/fast-mode), [Advisor](/en/advisor), [Channels](/en/channels), the [analytics dashboard](/en/analytics), and [server-managed settings](/en/server-managed-settings).

    **Partial support:**

* [Desktop](/en/desktop): only via [Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview)
* [Auto mode](/en/auto-mode-config): Sonnet 5, Opus 4.7, and Opus 4.8 only
* [`/loop`](/en/scheduled-tasks): explicit intervals only
* [Zero Data Retention](/en/zero-data-retention): subject to your AWS agreement

    **Alternatives:** for scheduling, use [`/loop`](/en/scheduled-tasks) with an explicit interval instead of `/schedule`. For cloud sessions, use [GitHub Actions](/en/github-actions) or [GitLab CI/CD](/en/gitlab-ci-cd). For web lookups, use the [WebFetch tool](/en/tools-reference#webfetch-tool-behavior) with a specific URL.



**Claude Platform on AWS**

    **Not available:** all [features that require a Claude subscription](#features-that-require-a-claude-subscription), plus [fast mode](/en/fast-mode), [Advisor](/en/advisor), [Channels](/en/channels), the [analytics dashboard](/en/analytics), and [server-managed settings](/en/server-managed-settings).

    **Available where Amazon Bedrock is not:** [web search](/en/tools-reference#websearch-tool-behavior) and [`/loop` self-pacing](/en/scheduled-tasks).

    **Alternatives:** for scheduling, use [`/loop`](/en/scheduled-tasks) instead of `/schedule`. For cloud sessions, use [GitHub Actions](/en/github-actions) or [GitLab CI/CD](/en/gitlab-ci-cd).



**Google Cloud's Agent Platform**

    **Not available:** all [features that require a Claude subscription](#features-that-require-a-claude-subscription), plus [fast mode](/en/fast-mode), [Advisor](/en/advisor), [Channels](/en/channels), the [analytics dashboard](/en/analytics), and [server-managed settings](/en/server-managed-settings).

    **Partial support:**

* [Desktop](/en/desktop): via [managed settings](https://support.claude.com/en/articles/12622667-enterprise-configuration) or [Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview)
* [Web search](/en/tools-reference#websearch-tool-behavior): Claude 4 models and later
* [Auto mode](/en/auto-mode-config): Sonnet 5, Opus 4.7, and Opus 4.8 only
* [`/loop`](/en/scheduled-tasks): explicit intervals only
* [Zero Data Retention](/en/zero-data-retention): subject to your Google Cloud agreement

    **Alternatives:** for scheduling, use [`/loop`](/en/scheduled-tasks) with an explicit interval instead of `/schedule`. For cloud sessions, use [GitHub Actions](/en/github-actions) or [GitLab CI/CD](/en/gitlab-ci-cd).



**Microsoft Foundry**

    **Not available:** all [features that require a Claude subscription](#features-that-require-a-claude-subscription), plus [fast mode](/en/fast-mode), [Advisor](/en/advisor), [Channels](/en/channels), [GitHub Actions](/en/github-actions) and [GitLab CI/CD](/en/gitlab-ci-cd), the [analytics dashboard](/en/analytics), and [server-managed settings](/en/server-managed-settings).

    **Partial support:**

* [Desktop](/en/desktop): only via [Claude Desktop on 3P](https://claude.com/docs/third-party/claude-desktop/overview)
* [Auto mode](/en/auto-mode-config): Sonnet 5, Opus 4.7, and Opus 4.8 only
* [`/loop`](/en/scheduled-tasks): explicit intervals only
* [Zero Data Retention](/en/zero-data-retention): subject to your Azure agreement

    **Alternatives:** for scheduling, use [`/loop`](/en/scheduled-tasks) with an explicit interval instead of `/schedule`.



**Anthropic Console**

    **Not available:** all [features that require a Claude subscription](#features-that-require-a-claude-subscription).

Everything in [CLI capabilities that vary by provider](#cli-capabilities-that-vary-by-provider) is available, as are [server-managed settings](/en/server-managed-settings) when the API key belongs to a Team or Enterprise organization.


## Availability by subscription plan

If you authenticate through Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, or an Anthropic Console API key, this section does not apply to you. When you sign in with a claude.ai account, your plan determines which of the features below are available.

| Feature                                                                                 | Pro | Max | Team          | Enterprise                        |
| :-------------------------------------------------------------------------------------- | :-- | :-- | :------------ | :-------------------------------- |
| [Claude Code on the web](/en/claude-code-on-the-web)                                    | ✓   | ✓   | ✓             | ✓ <sup>[6](#fn6)</sup> |
| [Routines](/en/routines)                                                                | ✓   | ✓   | ✓             | ✓                                 |
| [Remote Control](/en/remote-control)                                                    | ✓   | ✓   | Admin-enabled | Admin-enabled                     |
| [Channels](/en/channels)                                                                | ✓   | ✓   | Admin-enabled | Admin-enabled                     |
| [Computer use](/en/computer-use)                                                        | ✓   | ✓   | ✗             | ✗                                 |
| Dispatch ([Desktop](/en/desktop#sessions-from-dispatch))                                | ✓   | ✓   | ✗             | ✗                                 |
| [Code Review](/en/code-review)                                                          | ✗   | ✗   | ✓             | ✓                                 |
| [Artifacts](/en/artifacts)                                                              | ✓   | ✓   | ✓             | Admin-enabled                     |
| [Analytics dashboard and contribution metrics](/en/analytics)                           | ✗   | ✗   | ✓             | ✓                                 |
| [Enterprise Analytics API](/en/analytics#access-data-programmatically)                  | ✗   | ✗   | ✗             | ✓                                 |
| [Server-managed settings](/en/server-managed-settings)                                  | ✗   | ✗   | ✓             | ✓                                 |
| [SSO](https://support.claude.com/en/articles/9266767-what-is-the-team-plan)             | ✗   | ✗   | ✓             | ✓                                 |
| SCIM                                                                                    | ✗   | ✗   | ✗             | ✓                                 |
| [Compliance API](https://platform.claude.com/docs/en/api/admin-api/compliance/overview) | ✗   | ✗   | ✗             | ✓                                 |
| [Zero Data Retention](/en/zero-data-retention)                                          | ✗   | ✗   | ✗             | ✓ <sup>[7](#fn7)</sup> |

<sup>7</sup> Not included in the standard Enterprise plan. Requires separate enablement by Anthropic for qualified accounts. See [Zero Data Retention](/en/zero-data-retention).

For pricing and the full plan comparison, see [Team plans](https://support.claude.com/en/articles/9266767-what-is-the-team-plan) and [Enterprise plans](https://support.claude.com/en/articles/9797531-what-is-the-enterprise-plan).

## Model availability

For which Claude models and context-window sizes are available per provider and region, see [Model configuration](/en/model-config) and the [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview). Vision, PDF input, and extended thinking are model capabilities rather than Claude Code features and work on every provider that offers the model. [Prompt caching](/en/prompt-caching) works the same way on most providers; on Amazon Bedrock, support varies by model.

## Related resources

* [Enterprise deployment overview](/en/third-party-integrations): compare authentication, billing, and regions across providers
* Provider setup guides: [Amazon Bedrock](/en/amazon-bedrock), [Claude Platform on AWS](/en/claude-platform-on-aws), [Google Cloud's Agent Platform](/en/google-vertex-ai), [Microsoft Foundry](/en/microsoft-foundry)
* [Platforms and integrations](/en/platforms): where Claude Code runs, including the CLI, Desktop, IDE extensions, web, mobile, and CI/CD
