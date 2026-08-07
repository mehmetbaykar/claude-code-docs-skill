"""Offline tests for the claude-code-docs fetcher."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import fetch_claude_code_docs as fetcher  # noqa: E402


@pytest.mark.parametrize(
    "url",
    [
        "https://code.claude.com/docs/en/hooks",
        "https://code.claude.com/docs/en/agent-sdk/python",
        "https://code.claude.com/docs/en/whats-new/2026-w19",
        "https://code.claude.com/docs/en/hooks.md",
        "https://code.claude.com/docs/en/hooks/",
    ],
)
def test_keeps_documentation_urls(url: str) -> None:
    assert fetcher.is_claude_code_doc_url(url) is True


@pytest.mark.parametrize(
    "url",
    [
        "https://code.claude.com/docs/es/hooks",
        "https://code.claude.com/docs/en/api/messages",
        "https://code.claude.com/docs/en/reference/anything",
        "https://code.claude.com/docs/en/legacy/old",
        "https://code.claude.com/pricing",
        "https://example.com/docs/en/hooks",
        "https://code.claude.com/docs/en/hooks?theme=dark",
    ],
)
def test_drops_out_of_scope_urls(url: str) -> None:
    assert fetcher.is_claude_code_doc_url(url) is False


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/docs/en/hooks", "hooks.md"),
        ("/docs/en/agent-sdk/python", "agent-sdk__python.md"),
        ("/docs/en/whats-new/2026-w19", "whats-new__2026-w19.md"),
        ("/en/docs/claude-code/hooks", "hooks.md"),
    ],
)
def test_path_to_filename(path: str, expected: str) -> None:
    assert fetcher.path_to_filename(path) == expected


def test_pages_from_paths_detects_slug_collisions() -> None:
    with pytest.raises(RuntimeError, match="Slug collision"):
        fetcher.pages_from_paths({"/docs/en/agent-sdk/python", "/docs/en/agent-sdk__python"})


def test_pages_from_paths_is_sorted_and_absolute() -> None:
    pages = fetcher.pages_from_paths({"/docs/en/mcp", "/docs/en/hooks"})

    assert [page.path for page in pages] == ["/docs/en/hooks", "/docs/en/mcp"]
    assert pages[0].url == "https://code.claude.com/docs/en/hooks"
    assert pages[0].markdown_url == "https://code.claude.com/docs/en/hooks.md"


def test_absolutize_links_rewrites_root_relative_targets() -> None:
    content = "See [settings](/docs/en/settings#available-settings) for details."
    rewritten = fetcher.absolutize_links(content)

    assert "(https://code.claude.com/docs/en/settings#available-settings)" in rewritten


def test_absolutize_links_handles_labels_containing_brackets() -> None:
    content = "[`[hooks].matcher`](/docs/en/hooks#matcher)"
    rewritten = fetcher.absolutize_links(content)

    assert "(https://code.claude.com/docs/en/hooks#matcher)" in rewritten


def test_absolutize_links_leaves_absolute_and_protocol_relative_links_alone() -> None:
    content = "[a](https://code.claude.com/docs/en/mcp) [b](//cdn.example.com/x.png)"
    assert fetcher.absolutize_links(content) == content


def test_clean_mdx_absolutizes_markdown_links_outside_fences() -> None:
    raw = "# Settings\n\nSee [env vars](/docs/en/env-vars).\n\n```bash\ncurl /docs/en/x\n```\n"
    cleaned = fetcher.clean_mdx(raw)

    assert "(https://code.claude.com/docs/en/env-vars)" in cleaned
    assert "curl /docs/en/x" in cleaned


def test_yaml_quoted_preserves_non_ascii_titles() -> None:
    """Titles were JSON-escaped before, which leaked \\u sequences into frontmatter."""

    assert fetcher.yaml_quoted("Week 26 · June 22–26, 2026") == '"Week 26 · June 22–26, 2026"'


def test_frontmatter_keeps_unicode_and_quotes_colons() -> None:
    page = fetcher.ClaudeCodePage(
        url="https://code.claude.com/docs/en/whats-new/2026-w26",
        path="/docs/en/whats-new/2026-w26",
        filename="whats-new__2026-w26.md",
        title="Week 26 · June 22–26, 2026",
    )
    frontmatter = fetcher.frontmatter_for(page, source_url=page.url)

    assert "\\u" not in frontmatter
    assert 'title: "Week 26 · June 22–26, 2026"' in frontmatter


def test_guards_pass_on_a_healthy_run() -> None:
    assert (
        fetcher.check_coverage_guards(
            discovered=183, live=183, stale=0, skipped=0, previous_file_count=183
        )
        == []
    )


def test_guards_fail_when_nothing_is_live() -> None:
    problems = fetcher.check_coverage_guards(
        discovered=183, live=0, stale=183, skipped=0, previous_file_count=183
    )
    assert any("No page was fetched live" in problem for problem in problems)


def test_guards_fail_when_discovery_collapses() -> None:
    """A truncated sitemap must not delete most of the mirror."""

    problems = fetcher.check_coverage_guards(
        discovered=20, live=20, stale=0, skipped=0, previous_file_count=183
    )
    assert any("refusing to delete references" in problem for problem in problems)


def test_guards_fail_on_empty_discovery() -> None:
    assert fetcher.check_coverage_guards(
        discovered=0, live=0, stale=0, skipped=0, previous_file_count=183
    ) == ["Discovery returned no documentation pages"]


def test_guards_tolerate_a_single_stale_page() -> None:
    assert (
        fetcher.check_coverage_guards(
            discovered=183, live=182, stale=1, skipped=0, previous_file_count=183
        )
        == []
    )
