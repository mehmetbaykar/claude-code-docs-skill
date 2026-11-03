#!/usr/bin/env python3
"""Mirror the Claude Code documentation into the claude-code-docs skill.

Product-specific settings only; the shared engine lives in docs_mirror.py.
"""

from __future__ import annotations

import re

from docs_mirror import Page, Product, Section, run


BASE_URL = "https://code.claude.com"

DOCUMENTATION_INDEX_HEADER = re.compile(
    r"\A>\s*##\s*Documentation Index\s*\n"
    r">\s*Fetch the complete documentation index at:[^\n]*\n"
    r">\s*Use this file to discover all available pages[^\n]*\n+"
)


def clean(page: Page, content: str) -> str:
    """Drop the llms.txt pointer Claude Code prepends to every Markdown page."""

    return DOCUMENTATION_INDEX_HEADER.sub("", content, count=1)


PRODUCT = Product(
    name="Claude Code",
    skill="claude-code-docs",
    repository="mehmetbaykar/claude-code-docs-skill",
    docs_url=f"{BASE_URL}/docs/en/",
    base_url=BASE_URL,
    sitemap_urls=(f"{BASE_URL}/docs/sitemap.xml",),
    llms_txt_url=f"{BASE_URL}/docs/llms.txt",
    sections=(
        Section(
            key="docs",
            label="Documentation",
            path_prefix="/docs/en",
            fetch="markdown",
            mdx=True,
        ),
    ),
    # Defensive: non-core subtrees that must never enter the mirror.
    excluded_prefixes=(
        "/docs/en/tool-use/",
        "/docs/en/examples/",
        "/docs/en/legacy/",
        "/docs/en/api/",
        "/docs/en/reference/",
    ),
    clean=clean,
)


if __name__ == "__main__":
    raise SystemExit(run(PRODUCT))
