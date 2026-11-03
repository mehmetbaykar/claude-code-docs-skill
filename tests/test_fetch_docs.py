"""Offline tests for the Claude Code product settings in fetch_docs.py."""

from __future__ import annotations

import pytest

import docs_mirror as dm
import fetch_docs


PRODUCT = fetch_docs.PRODUCT


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
    assert dm.page_path(PRODUCT, url) is not None


@pytest.mark.parametrize(
    "url",
    [
        "https://code.claude.com/docs/es/hooks",
        "https://code.claude.com/docs/en",
        "https://code.claude.com/docs/en/api/messages",
        "https://code.claude.com/docs/en/reference/anything",
        "https://code.claude.com/docs/en/legacy/old",
        "https://code.claude.com/pricing",
        "https://example.com/docs/en/hooks",
        "https://code.claude.com/docs/en/hooks?theme=dark",
    ],
)
def test_drops_out_of_scope_urls(url: str) -> None:
    assert dm.page_path(PRODUCT, url) is None


def test_llms_index_spelling_maps_to_the_section_page() -> None:
    url = "https://code.claude.com/docs/en/whats-new/index.md"
    assert dm.page_path(PRODUCT, url, strip_query=True) == "/docs/en/whats-new"


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/docs/en/hooks", "hooks.md"),
        ("/docs/en/agent-sdk/python", "agent-sdk__python.md"),
        ("/docs/en/whats-new/2026-w19", "whats-new__2026-w19.md"),
    ],
)
def test_filenames_stay_stable_for_installed_skills(path: str, expected: str) -> None:
    assert dm.pages_from_paths(PRODUCT, {path})[0].filename == expected


def test_clean_drops_the_documentation_index_header() -> None:
    raw = (
        "> ## Documentation Index\n"
        "> Fetch the complete documentation index at: https://code.claude.com/docs/llms.txt\n"
        "> Use this file to discover all available pages before exploring further.\n\n"
        "# Hooks\n\nBody.\n"
    )
    page = dm.pages_from_paths(PRODUCT, {"/docs/en/hooks"})[0]
    assert fetch_docs.clean(page, raw) == "# Hooks\n\nBody.\n"


def test_clean_keeps_pages_without_the_header() -> None:
    page = dm.pages_from_paths(PRODUCT, {"/docs/en/hooks"})[0]
    assert fetch_docs.clean(page, "# Hooks\n\n> A quote.\n") == "# Hooks\n\n> A quote.\n"
