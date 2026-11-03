#!/usr/bin/env python3
"""Shared engine behind the docs-skill documentation mirrors.

This file is byte-identical in three repositories:

- mehmetbaykar/claude-code-docs-skill
- mehmetbaykar/codex-docs-skill
- mehmetbaykar/cursor-docs-skill

Each repository describes its product in ``scripts/fetch_docs.py``. Discovery,
fetching, cleaning, validation, and publishing live here. The CI drift check
fails when a shared file differs between the repositories, so change shared
files in all three at once.

A run stages every page in memory and checks the coverage guards before it
touches disk, so a failed run leaves the committed mirror exactly as it was.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import logging
import os
import random
import re
import time
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify


ROOT_DIR = Path(__file__).resolve().parent.parent
MANIFEST_FILE = "docs_manifest.json"
INDEX_FILE = "INDEX.md"
RAW_DIR_NAME = "_raw"
FETCH_TOOL_VERSION = "3.0"

MAX_RETRIES = 3
REQUEST_TIMEOUT = 30
RATE_LIMIT_SECONDS = 0.2
RETRY_BASE_DELAY_SECONDS = 1
RETRY_MAX_DELAY_SECONDS = 10
MAX_THROTTLE_RETRIES = 5

# Coverage guards. A mirror that silently keeps serving old content is worse
# than one that fails loudly, so the run fails when live coverage collapses.
MAX_STALE_RATIO = 0.2
MAX_SKIPPED_RATIO = 0.2
MAX_RAW_FALLBACK_RATIO = 0.2
MIN_DISCOVERY_RATIO = 0.8

# Converted HTML must keep this much text and at least one heading. Anything
# less means the site layout changed and the selector lost the article.
MIN_HTML_MARKDOWN_CHARS = 200

ACCEPT_TEXT = "text/plain, text/markdown, application/xml, text/xml, */*"
# Some sites serve Markdown for a page path only when the request prefers it.
ACCEPT_NEGOTIATED_MARKDOWN = "text/markdown,text/plain,*/*"
ACCEPT_HTML = "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"

# Links to these files are assets or indexes, not documentation pages.
NON_PAGE_SUFFIXES = {".txt", ".xml", ".json", ".yaml", ".yml", ".pdf", ".zip"}

# Version fields kept in step with the mirror, so plugin hosts that cache by
# version see every documentation refresh.
PLUGIN_MANIFESTS = (
    "plugin.json",
    ".claude-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
)

SIBLING_REPOSITORIES = (
    "mehmetbaykar/claude-code-docs-skill",
    "mehmetbaykar/codex-docs-skill",
    "mehmetbaykar/cursor-docs-skill",
)
SHARED_FILES = (
    ".github/dependabot.yml",
    ".github/workflows/update-docs.yml",
    "scripts/docs_mirror.py",
    "scripts/requirements-dev.txt",
    "scripts/requirements.txt",
    "tests/conftest.py",
    "tests/test_docs_mirror.py",
    "tests/test_repository.py",
)

logger = logging.getLogger("docs-mirror")


# --------------------------------------------------------------------------
# Product description
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Section:
    """A family of pages mirrored from the product site.

    ``fetch`` selects how a page is retrieved: ``markdown`` reads the ``.md``
    twin of the page URL, ``negotiate`` asks the page URL for Markdown through
    the Accept header, and ``html`` converts the element matched by
    ``html_selector``. ``keep_prefix`` prefixes filenames with the section
    path, and ``root_filename`` names the page at the prefix itself (``None``
    leaves that page out).
    """

    key: str
    label: str
    path_prefix: str
    fetch: str = "markdown"
    mdx: bool = False
    keep_prefix: bool = False
    root_filename: str | None = None
    html_selector: str | None = None


@dataclass(frozen=True)
class Page:
    url: str
    path: str
    filename: str
    title: str
    section: Section


def _same_path(path: str) -> str:
    return path


def _same_content(page: Page, content: str) -> str:
    return content


@dataclass(frozen=True)
class Product:
    """Everything product-specific about one mirror.

    ``map_path`` rewrites legacy paths found in indexes and links, ``clean``
    removes upstream boilerplate before the shared cleaning runs, ``exclude``
    returns a reason to drop a fetched page, and ``special`` maps a path to a
    custom fetcher returning ``(markdown, source_url)``.
    """

    name: str
    skill: str
    repository: str
    docs_url: str
    base_url: str
    sitemap_urls: tuple[str, ...]
    llms_txt_url: str | None
    sections: tuple[Section, ...]
    alternate_hosts: tuple[str, ...] = ()
    excluded_prefixes: tuple[str, ...] = ()
    excluded_paths: tuple[str, ...] = ()
    map_path: Callable[[str], str] = _same_path
    clean: Callable[[Page, str], str] = _same_content
    exclude: Callable[[Page, str], str | None] | None = None
    special: dict[str, Callable[[requests.Session, Product, Page], tuple[str, str]]] = field(
        default_factory=dict
    )
    source_extra: dict[str, str] = field(default_factory=dict)

    @property
    def host(self) -> str:
        return urlparse(self.base_url).netloc

    def references_dir(self, root: Path) -> Path:
        return root / "skills" / self.skill / "references"


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def sanitize_error(error: Exception) -> str:
    """Render an exception without leaking local paths or credentials.

    Error text can end up in logs and the committed manifest, so a maintainer
    running the fetcher locally must not publish their home directory, their
    operating system username, or credentials embedded in a proxy URL.
    """

    message = f"{type(error).__name__}: {error}"
    message = re.sub(r"//[^/@\s]+:[^/@\s]+@", "//<redacted>@", message)
    message = message.replace(str(ROOT_DIR), "<repo>")
    message = message.replace(str(Path.home()), "<home>")
    message = re.sub(r"/(Users|home)/[^/\s'\"]+", r"/\1/<user>", message)
    return message[:300]


def yaml_quoted(value: str) -> str:
    """Quote a YAML scalar without escaping non-ASCII characters."""

    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def frontmatter_for(page: Page, title: str) -> str:
    return (
        "---\n"
        f"title: {yaml_quoted(title)}\n"
        f"source: {page.url}\n"
        f"path: {page.path}\n"
        "---\n\n"
    )


def extract_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return fallback


def plugin_version(timestamp: str) -> str:
    """Turn a mirror timestamp into a monotonic semantic version.

    ``2026-11-03T15:34:00+00:00`` becomes ``2026.1103.1534``: year, then
    month and day, then hour and minute, with no leading zeros.
    """

    moment = datetime.fromisoformat(timestamp).astimezone(timezone.utc)
    return f"{moment.year}.{moment.month * 100 + moment.day}.{moment.hour * 100 + moment.minute}"


def write_text_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------


def http_headers(product: Product, accept: str) -> dict[str, str]:
    return {
        "User-Agent": (
            f"{product.skill}-skill-fetcher/{FETCH_TOOL_VERSION} "
            f"(+{product.docs_url})"
        ),
        "Accept": accept,
        "Cache-Control": "no-cache",
    }


def _sleep_backoff(url: str, attempt: int, error: Exception) -> None:
    delay = min(RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1)), RETRY_MAX_DELAY_SECONDS)
    delay *= random.uniform(0.5, 1.0)
    logger.warning(
        "Fetch failed for %s (%s/%s): %s; retrying in %.1fs",
        url,
        attempt,
        MAX_RETRIES,
        error,
        delay,
    )
    time.sleep(delay)


def request(
    session: requests.Session,
    url: str,
    *,
    headers: dict[str, str],
    allow_404: bool = False,
) -> requests.Response | None:
    """Fetch a URL, retrying transient failures with jittered backoff.

    Returns None only when ``allow_404`` is set and the server replied 404.
    Other 4xx responses raise immediately because they are not transient. 5xx,
    connection, and timeout errors retry; 429 honors ``Retry-After`` (or 30s)
    and does not consume an attempt.
    """

    last_error: Exception | None = None
    attempt = 0
    throttle_count = 0
    while attempt < MAX_RETRIES:
        attempt += 1
        try:
            response = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        except (
            requests.ConnectionError,
            requests.Timeout,
            requests.exceptions.ChunkedEncodingError,
        ) as error:
            last_error = error
            _sleep_backoff(url, attempt, error)
            continue

        if response.status_code == 404 and allow_404:
            return None
        if response.status_code == 429:
            if throttle_count >= MAX_THROTTLE_RETRIES:
                raise RuntimeError(
                    f"Rate limited fetching {url} after {MAX_THROTTLE_RETRIES} cooperative retries"
                )
            throttle_count += 1
            wait_seconds = int(response.headers.get("Retry-After", "30"))
            logger.warning(
                "Rate limited fetching %s; waiting %ss (cooperative retry %s/%s)",
                url,
                wait_seconds,
                throttle_count,
                MAX_THROTTLE_RETRIES,
            )
            time.sleep(wait_seconds)
            attempt -= 1
            continue
        if 500 <= response.status_code < 600:
            error = requests.HTTPError(f"{response.status_code} {response.reason}", response=response)
            last_error = error
            _sleep_backoff(url, attempt, error)
            continue

        response.raise_for_status()
        return response

    raise RuntimeError(f"Failed to fetch {url} after {MAX_RETRIES} attempts: {last_error}")


def fetch_text(
    session: requests.Session,
    product: Product,
    url: str,
    *,
    allow_404: bool = False,
    accept: str = ACCEPT_TEXT,
) -> str | None:
    response = request(session, url, headers=http_headers(product, accept), allow_404=allow_404)
    return None if response is None else response.text


def parse_xml(text: str) -> ET.Element:
    """Parse a sitemap or feed. DTDs are refused, so entity tricks cannot apply."""

    if re.search(r"<!(?:DOCTYPE|ENTITY)", text[:4096], flags=re.IGNORECASE):
        raise RuntimeError("Refusing to parse XML that declares a DTD or entities")
    try:
        return ET.fromstring(text)
    except ET.ParseError as error:
        raise RuntimeError(f"Failed to parse XML: {error}") from error


# --------------------------------------------------------------------------
# Discovery
# --------------------------------------------------------------------------


def normalize_path(path: str) -> str:
    path = re.sub(r"/{2,}", "/", path) or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    for suffix in (".md", ".html"):
        if path.endswith(suffix):
            path = path.removesuffix(suffix)
    # llms.txt files sometimes spell a section landing page as `<section>/index`.
    if path.endswith("/index"):
        path = path.removesuffix("/index") or "/"
    return path


def section_for(product: Product, path: str) -> Section | None:
    best: Section | None = None
    for section in product.sections:
        prefix = section.path_prefix
        if path == prefix or path.startswith(f"{prefix}/"):
            if best is None or len(prefix) > len(best.path_prefix):
                best = section
    return best


def page_path(product: Product, url: str, *, strip_query: bool = False) -> str | None:
    """Return the mirrored path for a URL, or None when the URL is out of scope."""

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return None
    if parsed.netloc != product.host and parsed.netloc not in product.alternate_hosts:
        return None
    if parsed.query and not strip_query:
        return None

    path = product.map_path(normalize_path(parsed.path))
    if PurePosixPath(path).suffix.lower() in NON_PAGE_SUFFIXES:
        return None
    section = section_for(product, path)
    if section is None:
        return None
    if path in product.excluded_paths or path.startswith(product.excluded_prefixes):
        return None
    if path == section.path_prefix and section.root_filename is None:
        return None
    return path


def filename_for(section: Section, path: str) -> str:
    if path == section.path_prefix:
        stem = section.root_filename or ""
    else:
        rest = path.removeprefix(section.path_prefix).strip("/")
        stem = f"{section.path_prefix.strip('/')}/{rest}" if section.keep_prefix else rest
    stem = stem.replace("/", "__")
    stem = re.sub(r"[^a-zA-Z0-9_.-]+", "-", stem).strip("-._").lower()
    if not stem:
        raise RuntimeError(f"Cannot derive a filename for {path!r}")
    return f"{stem}.md"


def title_from_path(section: Section, path: str) -> str:
    stem = filename_for(section, path).removesuffix(".md")
    return " ".join(part.capitalize() for part in re.split(r"[_-]+", stem) if part)


def pages_from_paths(product: Product, paths: set[str]) -> list[Page]:
    pages: list[Page] = []
    filename_to_path: dict[str, str] = {}
    for path in sorted(paths):
        section = section_for(product, path)
        if section is None:
            continue
        filename = filename_for(section, path)
        prior_path = filename_to_path.get(filename)
        if prior_path is not None and prior_path != path:
            raise RuntimeError(
                f"Slug collision: {prior_path!r} and {path!r} both map to {filename!r}"
            )
        filename_to_path[filename] = path
        pages.append(
            Page(
                url=f"{product.base_url}{path}",
                path=path,
                filename=filename,
                title=title_from_path(section, path),
                section=section,
            )
        )
    return pages


def sitemap_locs(
    session: requests.Session, product: Product, url: str, depth: int = 0
) -> list[str]:
    """Return page URLs listed by a sitemap, following nested sitemaps."""

    logger.info("Fetching sitemap: %s", url)
    try:
        text = fetch_text(session, product, url, allow_404=True)
    except (RuntimeError, requests.RequestException) as error:
        logger.warning("Failed to fetch sitemap %s: %s", url, error)
        return []
    if not text:
        return []

    locs: list[str] = []
    for element in parse_xml(text).iter():
        if not (element.tag.endswith("loc") and element.text):
            continue
        loc = element.text.strip()
        if loc.endswith(".xml") and depth < 2:
            locs.extend(sitemap_locs(session, product, loc, depth + 1))
        else:
            locs.append(loc)
    return locs


LINK_PATTERN = re.compile(r"https?://[^\s)\]>\"'`]+")


def llms_links(session: requests.Session, product: Product) -> list[str]:
    if not product.llms_txt_url:
        return []
    logger.info("Fetching llms.txt: %s", product.llms_txt_url)
    try:
        text = fetch_text(session, product, product.llms_txt_url, allow_404=True)
    except (RuntimeError, requests.RequestException) as error:
        logger.warning("Failed to fetch %s: %s", product.llms_txt_url, error)
        return []
    return LINK_PATTERN.findall(text or "")


def discover(session: requests.Session, product: Product) -> list[Page]:
    """Merge the sitemaps with llms.txt; neither index is complete on its own."""

    paths: set[str] = set()
    for sitemap_url in product.sitemap_urls:
        for loc in sitemap_locs(session, product, sitemap_url):
            path = page_path(product, loc)
            if path:
                paths.add(path)
    from_sitemaps = len(paths)

    # llms.txt links some pages only as query variants of a shared page (for
    # example `?surface=cli`), so the query is dropped and the page kept once.
    for link in llms_links(session, product):
        path = page_path(product, link, strip_query=True)
        if path:
            paths.add(path)

    pages = pages_from_paths(product, paths)
    logger.info(
        "Discovered %s pages (%s from sitemaps, %s more from llms.txt)",
        len(pages),
        from_sitemaps,
        len(paths) - from_sitemaps,
    )
    return pages


# --------------------------------------------------------------------------
# Cleaning
# --------------------------------------------------------------------------


def _split_by_fences(text: str) -> list[tuple[bool, str]]:
    """Return ``(in_fence, chunk)`` segments split on triple-backtick lines.

    Fence delimiter lines come back as ``in_fence=False`` so outside-of-fence
    transforms leave them verbatim while still toggling the fenced state.
    """

    segments: list[tuple[bool, str]] = []
    buffer: list[str] = []
    in_fence = False

    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            if buffer:
                segments.append((in_fence, "".join(buffer)))
                buffer = []
            segments.append((False, line))
            in_fence = not in_fence
            continue
        buffer.append(line)

    if buffer:
        segments.append((in_fence, "".join(buffer)))
    return segments


def apply_outside_fences(text: str, transform: Callable[[str], str]) -> str:
    return "".join(
        chunk if in_fence else transform(chunk) for in_fence, chunk in _split_by_fences(text)
    )


# Inline code such as `CLAUDE_PLUGIN_OPTION_<KEY>` or `Array<Item>` looks like
# a component tag to the cleaning passes. Spans holding `<` are set aside while
# a pass runs and restored afterwards, so their placeholders survive.
CODE_SPAN = re.compile(r"`[^`\n]*`")


def protect_code_spans(text: str, transform: Callable[[str], str]) -> str:
    spans: list[str] = []

    def stash(match: re.Match[str]) -> str:
        if "<" not in match.group(0):
            return match.group(0)
        spans.append(match.group(0))
        return f"\x00{len(spans) - 1}\x00"

    # Matching every span left to right keeps backticks paired, so the text
    # between two spans is never mistaken for a span itself.
    result = transform(CODE_SPAN.sub(stash, text))
    return re.sub(r"\x00(\d+)\x00", lambda match: spans[int(match.group(1))], result)


def link_resolver(product: Product) -> Callable[[str], str]:
    """Return a function that turns a root-relative target into an absolute URL."""

    def resolve(target: str) -> str:
        path, separator, fragment = target.partition("#")
        mapped = product.map_path(path) if path else ""
        return f"{product.base_url}{mapped}{separator}{fragment}"

    return resolve


def absolutize_links(content: str, resolve: Callable[[str], str]) -> str:
    """Rewrite root-relative Markdown link targets to absolute URLs.

    Anchored on the target rather than the label, because labels can contain
    brackets (for example ``[`[auto_review].policy`](/docs/...)``).
    """

    return re.sub(
        r"\]\((?P<target>/(?!/)[^)\s]*)\)",
        lambda match: f"]({resolve(match.group('target'))})",
        content,
    )


def convert_html_links(content: str, resolve: Callable[[str], str]) -> str:
    def replace_anchor(match: re.Match[str]) -> str:
        href = html.unescape(match.group("href"))
        label = html.unescape(re.sub(r"<[^>]+>", "", match.group("label")).strip())
        if href.startswith("/") and not href.startswith("//"):
            href = resolve(href)
        return f"[{label}]({href})"

    return re.sub(
        r"<a\b[^>]*href=[\"'](?P<href>[^\"']+)[\"'][^>]*>(?P<label>.*?)</a>",
        replace_anchor,
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )


def convert_keyboard_tags(content: str) -> str:
    return re.sub(
        r"<kbd>(.*?)</kbd>",
        lambda match: f"`{html.unescape(match.group(1).strip())}`",
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )


def convert_admonition_blocks(content: str) -> str:
    """Unwrap MDX wrapper components without losing the content they carry.

    Inline single-line admonitions become GitHub-style alert blockquotes.
    Multi-line admonitions lose only their opening and closing tags, so the
    inner prose survives the later component-tag pass.
    """

    inline_admonitions = (
        (r"<Tip\b[^>]*>(.*?)</Tip>", r"> [!TIP] \1"),
        (r"<Note\b[^>]*>(.*?)</Note>", r"> [!NOTE] \1"),
        (r"<Warning\b[^>]*>(.*?)</Warning>", r"> [!WARNING] \1"),
        (r"<Info\b[^>]*>(.*?)</Info>", r"> [!INFO] \1"),
        (r"<Check\b[^>]*>(.*?)</Check>", r"> \1"),
    )
    for pattern, replacement in inline_admonitions:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

    for tag in ("Tab", "Card", "Accordion", "Expandable"):
        content = re.sub(
            rf'<{tag}\s+[^>]*?title="([^"]+)"[^>]*?>',
            r"\n**\1**\n",
            content,
            flags=re.IGNORECASE,
        )
        content = re.sub(rf"</{tag}>", "", content, flags=re.IGNORECASE)

    wrapper_only_tags = (
        "Tabs",
        "CardGroup",
        "AccordionGroup",
        "CodeGroup",
        "Frame",
        "Steps",
        "Tip",
        "Note",
        "Warning",
        "Info",
        "Check",
    )
    for tag in wrapper_only_tags:
        content = re.sub(rf"<{tag}\b[^>]*>", "", content, flags=re.IGNORECASE)
        content = re.sub(rf"</{tag}>", "", content, flags=re.IGNORECASE)
    return content


def strip_exported_component_blocks(content: str) -> str:
    lines = content.splitlines()
    cleaned: list[str] = []
    index = 0
    in_fence = False

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if stripped.startswith("```"):
            in_fence = not in_fence
            cleaned.append(line)
            index += 1
            continue

        if not in_fence and re.match(r"^export\s+const\s+\w+\s*=", stripped):
            brace_balance = line.count("{") - line.count("}")
            index += 1
            while index < len(lines):
                current = lines[index]
                brace_balance += current.count("{") - current.count("}")
                if brace_balance <= 0 and current.strip().endswith(";"):
                    index += 1
                    break
                index += 1
            continue

        if not in_fence and re.match(r"^<ContactSalesCard\b[^>]*/>\s*$", stripped):
            index += 1
            continue

        cleaned.append(line)
        index += 1

    return "\n".join(cleaned)


def convert_html_text_tags(content: str) -> str:
    replacements = (
        (r"<code\b[^>]*>(.*?)</code>", r"`\1`"),
        (r"<strong\b[^>]*>(.*?)</strong>", r"**\1**"),
        (r"<em\b[^>]*>(.*?)</em>", r"*\1*"),
        (r"<p\b[^>]*>(.*?)</p>", r"\1"),
        (r"<span\b[^>]*>(.*?)</span>", r"\1"),
        (r"<div\b[^>]*>(.*?)</div>", r"\1"),
    )
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE | re.DOTALL)
    return content


def convert_html_tables(content: str) -> str:
    def convert_table(match: re.Match[str]) -> str:
        rows: list[list[str]] = []
        for row_match in re.finditer(
            r"<tr\b[^>]*>(.*?)</tr>", match.group(0), flags=re.IGNORECASE | re.DOTALL
        ):
            cells: list[str] = []
            for cell_match in re.finditer(
                r"<t[dh]\b[^>]*>(.*?)</t[dh]>", row_match.group(1), flags=re.IGNORECASE | re.DOTALL
            ):
                cell = re.sub(r"<br\s*/?>", " ", cell_match.group(1), flags=re.IGNORECASE)
                cell = html.unescape(re.sub(r"<[^>]+>", "", cell))
                cells.append(re.sub(r"\s+", " ", cell).strip().replace("|", "\\|"))
            if cells:
                rows.append(cells)

        if not rows:
            return ""
        width = max(len(row) for row in rows)
        rows = [row + [""] * (width - len(row)) for row in rows]
        markdown = [
            "| " + " | ".join(rows[0]) + " |",
            "| " + " | ".join("---" for _ in rows[0]) + " |",
        ]
        markdown.extend("| " + " | ".join(row) + " |" for row in rows[1:])
        return "\n" + "\n".join(markdown) + "\n"

    return re.sub(
        r"<table\b[^>]*>.*?</table>", convert_table, content, flags=re.IGNORECASE | re.DOTALL
    )


def strip_inline_markdown_noise(content: str) -> str:
    content = content.replace('{" "}', " ").replace("{' '}", " ")
    return re.sub(r"\{`([^`]+)`\}", r"`\1`", content)


def remove_component_tags(content: str) -> str:
    cleaned: list[str] = []
    in_fence = False
    skipping_tag = False
    skipping_script = False

    for line in content.splitlines():
        stripped = line.strip()

        if stripped.startswith("```"):
            in_fence = not in_fence
            cleaned.append(line)
            continue
        if in_fence:
            cleaned.append(line)
            continue
        if skipping_script:
            if "</script>" in stripped.lower():
                skipping_script = False
            continue
        if skipping_tag:
            if ">" in stripped:
                skipping_tag = False
            continue
        if stripped.lower().startswith("<script"):
            if "</script>" not in stripped.lower():
                skipping_script = True
            continue
        if re.match(r"^</?[A-Z][A-Za-z0-9_.-]*\b", stripped):
            if not stripped.startswith("</") and ">" not in stripped:
                skipping_tag = True
            continue
        if re.match(r"^</?(div|span|br|section|aside)\b", stripped, flags=re.IGNORECASE):
            if stripped.startswith("</"):
                continue
            if stripped.endswith("/>") or stripped in {"<br>", "<br/>", "<br />"}:
                continue
            if ">" not in stripped:
                skipping_tag = True
                continue
            line = re.sub(r"</?(div|span|section|aside)\b[^>]*>", "", line, flags=re.IGNORECASE)
            if not line.strip():
                continue

        line = protect_code_spans(
            line,
            lambda text: re.sub(
                r"<br\s*/?>",
                "",
                re.sub(r"</?[A-Z][A-Za-z0-9_.-]*\b[^>]*>", "", text),
                flags=re.IGNORECASE,
            ),
        )
        cleaned.append(line)

    return "\n".join(cleaned)


def clean_fence_metadata(content: str) -> str:
    def replace_fence(match: re.Match[str]) -> str:
        extras = [
            token
            for token in (match.group("metadata") or "").split()
            if token and not token.startswith("theme=") and token != "terminal"
        ]
        suffix = f" {' '.join(extras)}" if extras else ""
        return f"{match.group('indent')}{match.group('fence')}{match.group('lang') or ''}{suffix}"

    return re.sub(
        r"^(?P<indent>[ \t]*)(?P<fence>`{3,})(?P<lang>[A-Za-z0-9_-]+)?(?P<metadata>[^\n`]*)$",
        replace_fence,
        content,
        flags=re.MULTILINE,
    )


LIST_ITEM = re.compile(r"^(?:[-*+]|\d+[.)])\s")


def normalize_markdown_indentation(content: str) -> str:
    """Remove the indentation MDX components leave behind, keeping list nesting.

    A run of indented lines that follows prose was indented by a component
    wrapper, so the whole run moves left by its first line's indentation and
    keeps its inner structure. A run that follows a list item is nested list
    content and stays where it is.
    """

    output: list[str] = []
    in_fence = False
    in_run = False
    after_list = False
    offset = 0
    for line in content.split("\n"):
        stripped = line.lstrip(" \t")
        indent = len(line) - len(stripped)
        if in_fence:
            if stripped.startswith("```"):
                in_fence = False
            output.append(line[min(offset, indent) :])
            continue
        if not stripped:
            output.append("")
            continue
        if indent < 2:
            in_run = False
            offset = 0
            after_list = bool(LIST_ITEM.match(stripped))
        elif not in_run:
            in_run = True
            offset = 0 if after_list else indent
        if stripped.startswith("```"):
            in_fence = True
        output.append(line[min(offset, indent) :])
    return "\n".join(output)


# MDX data components -------------------------------------------------------
#
# Some MDX pages are a single component whose props hold the whole page as
# JavaScript object literals, for example a section landing page or a
# glossary. Dropping the tag would leave an empty page, so the props are read
# as data and rendered as Markdown lists instead.

PRESENTATION_KEYS = {
    "active",
    "alt",
    "backgroundImage",
    "class",
    "className",
    "client:load",
    "collapsed",
    "color",
    "emptyStateMessage",
    "expanded",
    "hero",
    "hidden",
    "highlight",
    "icon",
    "id",
    "illustration",
    "image",
    "maxVisibleEntries",
    "open",
    "placeholder",
    "searchLabel",
    "searchPlaceholder",
    "selected",
    "theme",
    "variant",
    "video",
}
LABEL_KEYS = ("title", "key", "label", "name", "term")
DETAIL_KEYS = ("description", "definition", "comment", "summary")


class CleaningError(ValueError):
    """A page cannot be cleaned without losing content, so it keeps its raw source."""


def js_literal_to_python(expression: str) -> object:
    """Convert a JavaScript object or array literal to Python data.

    Handles unquoted keys, single-quoted strings, template literals without
    substitutions, and trailing commas, which is what generated docs pages
    use. Raises ValueError for anything else.
    """

    out: list[str] = []
    index = 0
    length = len(expression)
    while index < length:
        char = expression[index]
        if char in "\"'":
            end = index + 1
            buffer: list[str] = []
            while end < length and expression[end] != char:
                if expression[end] == "\\" and end + 1 < length:
                    escaped = expression[end + 1]
                    buffer.append("'" if escaped == "'" else expression[end : end + 2])
                    end += 2
                    continue
                buffer.append('\\"' if expression[end] == '"' else expression[end])
                end += 1
            if end >= length:
                raise ValueError("Unterminated string literal")
            out.append('"' + "".join(buffer) + '"')
            index = end + 1
            continue
        if char == "`":
            end = expression.find("`", index + 1)
            if end == -1 or "${" in expression[index + 1 : end]:
                raise ValueError("Template literals with substitutions are not supported")
            out.append(json.dumps(expression[index + 1 : end]))
            index = end + 1
            continue
        if char.isalpha() or char in "_$":
            word = re.match(r"[A-Za-z_$][\w$]*", expression[index:]).group(0)
            rest = expression[index + len(word) :].lstrip()
            if rest.startswith(":"):
                out.append(json.dumps(word))
            elif word in {"true", "false", "null"}:
                out.append(word)
            else:
                raise ValueError(f"Unsupported identifier {word!r}")
            index += len(word)
            continue
        if char == ",":
            if expression[index + 1 :].lstrip()[:1] in {"}", "]"}:
                index += 1
                continue
        out.append(char)
        index += 1
    return json.loads("".join(out))


def _read_balanced(text: str, start: int) -> int:
    """Return the index just past the brace group that opens at ``start``."""

    depth = 0
    index = start
    quote: str | None = None
    while index < len(text):
        char = text[index]
        if quote:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
        elif char in "\"'`":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    raise ValueError("Unbalanced braces in component props")


def parse_jsx_props(text: str) -> dict[str, object]:
    props: dict[str, object] = {}
    index = 0
    while index < len(text):
        if text[index].isspace():
            index += 1
            continue
        match = re.match(r"[A-Za-z_][\w:.-]*", text[index:])
        if not match:
            raise ValueError(f"Unexpected character {text[index]!r} in component props")
        name = match.group(0)
        index += len(name)
        if index < len(text) and text[index] == "=":
            index += 1
            if text[index] == '"':
                end = text.index('"', index + 1)
                props[name] = html.unescape(text[index + 1 : end])
                index = end + 1
            elif text[index] == "{":
                end = _read_balanced(text, index)
                props[name] = js_literal_to_python(text[index + 1 : end - 1].strip())
                index = end
            else:
                raise ValueError(f"Unsupported value for prop {name!r}")
        else:
            props[name] = True
    return props


def _opening_tag_end(text: str) -> tuple[int, bool] | None:
    """Find where a component's opening tag ends in the text after its name.

    Returns the offset just past the closing ``>`` and whether the tag is
    self-closing, or None when the tag never closes. Braces and quotes are
    respected, so a ``>`` inside a prop value does not end the tag.
    """

    depth = 0
    quote: str | None = None
    index = 0
    while index < len(text):
        char = text[index]
        if quote:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
        elif char in "\"'" or (char == "`" and depth > 0):
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif char == ">" and depth == 0:
            return index + 1, text[index - 1 : index] == "/"
        index += 1
    return None


def _humanize(key: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", " ", key).capitalize()


def _text(value: str) -> str:
    """Escape rendered data so tag removal keeps placeholders like `<Event>`.

    The cleaner unescapes entities after it removes component tags.
    """

    return html.escape(value, quote=False)


def _scalar(value: object) -> str | None:
    """Render a data value for an item's extras, or None when it is not a scalar."""

    if isinstance(value, str):
        return _text(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list) and value and all(isinstance(entry, (str, int, float)) for entry in value):
        return ", ".join(_scalar(entry) or "" for entry in value)
    return None


def _render_items(items: list[object], level: int, indent: str = "") -> list[str]:
    """Render component data: titled groups become headings, the rest nested bullets."""

    lines: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            rendered = _scalar(item)
            if rendered:
                lines.append(f"{indent}- {rendered}")
            continue
        label = _text(next((item[key] for key in LABEL_KEYS if isinstance(item.get(key), str)), ""))
        href = item.get("href") or item.get("url")
        detail = _text(next((item[key] for key in DETAIL_KEYS if isinstance(item.get(key), str)), ""))
        children = next(
            (
                value
                for value in item.values()
                if isinstance(value, list) and any(isinstance(entry, dict) for entry in value)
            ),
            None,
        )
        if children is not None and isinstance(item.get("title"), str) and not indent and level <= 4:
            lines.extend(["", f"{'#' * level} {label}", ""])
            if detail:
                lines.extend([detail, ""])
            lines.extend(_render_items(children, level + 1))
            continue

        text = f"[{label}]({href})" if label and isinstance(href, str) else label
        extras = [
            f"{_humanize(key)}: {rendered}"
            for key, value in item.items()
            if key not in {*LABEL_KEYS, *DETAIL_KEYS, "href", "url"}
            and key not in PRESENTATION_KEYS
            and (rendered := _scalar(value)) is not None
        ]
        line = f"{indent}- {text}" if text else f"{indent}-"
        if detail:
            line += f": {detail}" if text else f" {detail}"
        if extras:
            line += f" ({'; '.join(extras)})"
        if text or detail or extras:
            lines.append(line)
        if children is not None:
            lines.extend(_render_items(children, level, indent + "  "))
    return lines


def render_component_data(props: dict[str, object]) -> str:
    lines: list[str] = []
    for key in ("description", "intro"):
        if isinstance(props.get(key), str):
            lines.extend([_text(str(props[key])), ""])
    cta = props.get("primaryCta")
    if isinstance(cta, dict) and isinstance(cta.get("label"), str) and isinstance(cta.get("href"), str):
        lines.extend([f"[{_text(cta['label'])}]({cta['href']})", ""])
    for key, value in props.items():
        if key not in PRESENTATION_KEYS and isinstance(value, list):
            lines.extend(_render_items(value, level=2))
    return "\n".join(lines).strip()


def expand_data_components(content: str) -> str:
    """Render self-closing MDX components that carry list data as Markdown.

    Only a component whose opening tag closes itself and passes an array prop
    counts; containers with children are left to the tag pass. Raises
    CleaningError when such a component cannot be read, so the page keeps its
    raw source instead of silently losing the data.
    """

    lines = content.split("\n")
    output: list[str] = []
    index = 0
    in_fence = False
    while index < len(lines):
        line = lines[index]
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        opening = None if in_fence else re.match(r"^<([A-Z][A-Za-z0-9]*)\s*$", line)
        rest = "\n".join(lines[index + 1 :]) if opening else ""
        tag = _opening_tag_end(rest) if opening else None
        if opening and tag and tag[1] and re.search(r"=\s*\{\s*\[", rest[: tag[0]]):
            end, _ = tag
            try:
                props = parse_jsx_props(rest[: end - 2])
            except (ValueError, json.JSONDecodeError) as error:
                raise CleaningError(f"Cannot read <{opening.group(1)}> data: {error}") from error
            output.append(render_component_data(props))
            last = index + 1 + rest[:end].count("\n")
            tail = rest[:end].rsplit("\n", 1)[-1]
            remainder = lines[last][len(tail) :]
            if remainder.strip():
                output.append(remainder)
            index = last + 1
            continue
        output.append(line)
        index += 1
    return "\n".join(output)


def clean_mdx(content: str, resolve: Callable[[str], str]) -> str:
    content = expand_data_components(content)
    content = strip_exported_component_blocks(content)

    def components_and_html(text: str) -> str:
        text = re.sub(r'<Update\s+label="([^"]+)"\s+description="([^"]+)"\s*>', r"### \1 (\2)\n", text)
        text = re.sub(r"</Update>", "", text)
        text = re.sub(r'<Step\s+title="([^"]+)"\s*>', r"\n**\1**\n", text)
        text = re.sub(r"</Step>", "", text)
        text = re.sub(
            r'<img\s+[^>]*?src="([^"]+)"[^>]*?(?:alt="([^"]*)")?[^>]*?/?>',
            lambda match: f"\n![{html.unescape(match.group(2) or '')}]({html.unescape(match.group(1))})\n",
            text,
        )
        text = re.sub(
            r'<video\s+[^>]*?src="([^"]+)"[^>]*?/?>',
            lambda match: f"\nVideo: {html.unescape(match.group(1))}\n",
            text,
        )
        text = convert_admonition_blocks(text)
        text = convert_html_links(text, resolve)
        text = convert_html_text_tags(text)
        return convert_html_tables(text)

    def scripts_and_links(text: str) -> str:
        text = re.sub(r"(?ms)^import\s+.*?(?=^\S|\Z)", "", text)
        text = re.sub(r"(?ms)^export\s+.*?(?=^\S|\Z)", "", text)
        text = re.sub(r"(?is)<script\b[^>]*>.*?</script>", "", text)
        text = convert_html_links(text, resolve)
        text = convert_keyboard_tags(text)
        text = strip_inline_markdown_noise(text)
        return absolutize_links(text, resolve)

    content = apply_outside_fences(content, lambda text: protect_code_spans(text, components_and_html))
    content = apply_outside_fences(content, lambda text: protect_code_spans(text, scripts_and_links))
    content = remove_component_tags(content)
    content = html.unescape(content)
    content = clean_fence_metadata(content)
    return normalize_markdown_indentation(content)


def finish_markdown(content: str) -> str:
    content = re.sub(r"\n{3,}", "\n\n", content)
    content = re.sub(r"[ \t]+\n", "\n", content)
    return content.strip() + "\n"


def looks_like_markdown(content: str, *, strict: bool) -> bool:
    """Reject HTML, near-empty bodies, and (when strict) structureless text.

    The strict check exists to catch cleaning failures: a page whose cleaner
    dropped everything keeps a title at most, not headings, lists, or code.
    """

    stripped = content.strip()
    if len(stripped) < 50:
        return False
    head = stripped[:200].lower()
    if "<!doctype html" in head or "<html" in head:
        return False
    if not strict:
        return True
    indicators = ("# ", "## ", "### ", "- ", "* ", "1. ", "```", "[", "|", "> ")
    return sum(1 for line in stripped.splitlines() if line.lstrip().startswith(indicators)) >= 2


def html_to_markdown(document: str, *, url: str, selector: str) -> str:
    """Convert the main content element of an HTML page to Markdown."""

    soup = BeautifulSoup(document, "html.parser")
    node = soup.select_one(selector)
    if node is None:
        raise RuntimeError(f"Selector {selector!r} matched nothing; the page layout changed")
    for tag in node.select("script, style, noscript, template, svg, button, form, iframe, nav"):
        tag.decompose()
    # Root-relative targets stay as they are so the shared link pass can map
    # legacy paths; other relative targets resolve against the page URL.
    for element, attribute in [(anchor, "href") for anchor in node.find_all("a", href=True)] + [
        (image, "src") for image in node.find_all("img", src=True)
    ]:
        target = element[attribute]
        if not target.startswith(("/", "#")) and not urlparse(target).scheme:
            element[attribute] = urljoin(url, target)

    markdown = markdownify(str(node), heading_style="ATX", bullets="-")
    if not any(line.startswith("# ") for line in markdown.splitlines()):
        heading = soup.find("h1") or soup.find("title")
        title = heading.get_text(" ", strip=True) if heading else ""
        if title:
            markdown = f"# {title}\n\n{markdown.lstrip()}"
    return markdown


# --------------------------------------------------------------------------
# Fetching one page
# --------------------------------------------------------------------------


@dataclass
class Outcome:
    kind: str  # "live", "skipped", or "excluded"
    content: str = ""
    source_url: str = ""
    reason: str = ""
    raw: str | None = None  # upstream source kept under _raw/ when cleaning failed


PAGE_ERRORS = (
    RuntimeError,
    requests.RequestException,
    OSError,
    ValueError,
    KeyError,
    TypeError,
    ET.ParseError,
)


def fetch_source(session: requests.Session, product: Product, page: Page) -> tuple[str | None, str, str]:
    """Return ``(text, source_url, skip_reason)`` for a page."""

    section = page.section
    if section.fetch == "markdown":
        source_url = f"{page.url}.md"
        text = fetch_text(session, product, source_url, allow_404=True)
        return text, source_url, "" if text is not None else "No .md endpoint"

    if section.fetch == "negotiate":
        response = request(
            session,
            page.url,
            headers=http_headers(product, ACCEPT_NEGOTIATED_MARKDOWN),
            allow_404=True,
        )
        if response is None:
            return None, page.url, "No Markdown endpoint"
        content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
        if content_type not in {"text/markdown", "text/plain", ""}:
            return None, page.url, f"Non-Markdown response ({content_type})"
        return response.text, page.url, ""

    if section.fetch == "html":
        if not section.html_selector:
            raise RuntimeError(f"Section {section.key!r} needs an html_selector")
        document = fetch_text(session, product, page.url, accept=ACCEPT_HTML)
        return html_to_markdown(document or "", url=page.url, selector=section.html_selector), page.url, ""

    raise RuntimeError(f"Unknown fetch mode {section.fetch!r} for section {section.key!r}")


def process_page(session: requests.Session, product: Product, page: Page) -> Outcome:
    special = product.special.get(page.path)
    if special is not None:
        markdown, source_url = special(session, product, page)
        title = extract_title(markdown, page.title)
        return Outcome("live", frontmatter_for(page, title) + finish_markdown(markdown), source_url)

    raw, source_url, skip_reason = fetch_source(session, product, page)
    if raw is None:
        return Outcome("skipped", source_url=source_url, reason=skip_reason)
    raw = raw.replace("\r\n", "\n")

    if product.exclude is not None:
        reason = product.exclude(page, raw)
        if reason:
            return Outcome("excluded", source_url=source_url, reason=reason)

    section = page.section
    resolve = link_resolver(product)
    content = product.clean(page, raw)
    if section.mdx:
        try:
            content = clean_mdx(content, resolve)
        except CleaningError as error:
            logger.warning("%s on %s", error, page.path)
            content = ""  # fall through to the raw fallback below
    else:
        content = apply_outside_fences(content, lambda text: absolutize_links(text, resolve))
    content = finish_markdown(content)
    title = extract_title(content, extract_title(raw, page.title))

    if section.fetch == "html":
        has_heading = any(line.startswith("#") for line in content.splitlines())
        if len(content) < MIN_HTML_MARKDOWN_CHARS or not has_heading:
            raise RuntimeError("Converted HTML is too short or has no heading; the page layout changed")

    if looks_like_markdown(content, strict=section.mdx or section.fetch == "html"):
        return Outcome("live", frontmatter_for(page, title) + content, source_url)
    if not section.mdx:
        raise RuntimeError("Response did not look like documentation Markdown")

    logger.warning("Cleaning failed; keeping raw source for %s", page.path)
    fallback = (
        frontmatter_for(page, title)
        + "> Note: Cleaning failed for this page, so this file holds the raw upstream source.\n\n"
        + raw.strip()
        + "\n"
    )
    return Outcome("live", fallback, source_url, raw=raw)


# --------------------------------------------------------------------------
# Staging and publishing
# --------------------------------------------------------------------------


def load_manifest(references: Path) -> dict:
    path = references / MANIFEST_FILE
    if not path.exists():
        return {"files": {}}
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        logger.warning("Ignoring invalid manifest JSON: %s", error)
        return {"files": {}}
    if not isinstance(manifest.get("files"), dict):
        manifest["files"] = {}
    return manifest


def check_coverage_guards(
    *,
    discovered: int,
    live: int,
    stale: int,
    skipped: int,
    previous_file_count: int,
    raw_fallbacks: int = 0,
) -> list[str]:
    """Return the reasons this run must fail instead of publishing."""

    if discovered == 0:
        return ["Discovery returned no documentation pages"]

    problems: list[str] = []
    if live == 0:
        problems.append("No page was fetched live; the mirror would be frozen")
    if previous_file_count and discovered < previous_file_count * MIN_DISCOVERY_RATIO:
        problems.append(
            f"Discovered {discovered} pages, below {MIN_DISCOVERY_RATIO:.0%} of the "
            f"previous {previous_file_count}; refusing to delete references"
        )
    if stale > discovered * MAX_STALE_RATIO:
        problems.append(
            f"{stale}/{discovered} pages served stale content, above the "
            f"{MAX_STALE_RATIO:.0%} threshold"
        )
    if skipped > discovered * MAX_SKIPPED_RATIO:
        problems.append(
            f"{skipped}/{discovered} pages had no usable Markdown, above the "
            f"{MAX_SKIPPED_RATIO:.0%} threshold"
        )
    if raw_fallbacks > discovered * MAX_RAW_FALLBACK_RATIO:
        problems.append(
            f"Cleaning failed for {raw_fallbacks}/{discovered} pages, above the "
            f"{MAX_RAW_FALLBACK_RATIO:.0%} threshold; the cleaner likely regressed"
        )
    return problems


def build_index(product: Product, entries: dict[str, dict], skipped: list[dict]) -> str:
    lines = [
        f"# {product.name} Docs Index",
        "",
        f"Local mirror of the {product.name} documentation from {product.docs_url}.",
        "",
        (
            f"Invoke this skill with a topic: `/{product.skill} hooks` in Claude Code "
            f"or Cursor, `${product.skill} hooks` in Codex."
        ),
        "",
    ]
    for section in product.sections:
        names = sorted(name for name, entry in entries.items() if entry["section"] == section.key)
        if not names:
            continue
        lines.extend([f"## {section.label}", ""])
        for name in names:
            entry = entries[name]
            lines.append(f"- `{name.removesuffix('.md')}` - [{entry['title']}]({entry['original_url']})")
        lines.append("")
    if skipped:
        lines.extend(["## Skipped Pages", ""])
        lines.extend(f"- `{item['path']}` - {item['reason']}" for item in skipped)
    return "\n".join(lines).strip() + "\n"


def _projection(manifest: dict) -> dict:
    projection = dict(manifest)
    projection.pop("last_updated", None)
    projection.pop("fetch_metadata", None)
    return projection


@dataclass
class Staged:
    writes: dict[Path, str]
    deletes: list[Path]
    manifest: dict
    problems: list[str]


def stage(
    session: requests.Session,
    product: Product,
    pages: list[Page],
    previous: dict,
    *,
    root: Path,
) -> Staged:
    """Fetch every page and compute the full mirror without writing anything."""

    references = product.references_dir(root)
    raw_dir = references / RAW_DIR_NAME
    previous_files: dict[str, dict] = previous.get("files", {})
    writes: dict[Path, str] = {}
    entries: dict[str, dict] = {}
    skipped: list[dict] = []
    excluded: list[dict] = []
    failed: list[dict] = []
    stale: list[dict] = []
    live = 0
    raw_fallbacks = 0

    def record(page: Page, content: str, source_url: str, status: str, has_raw: bool) -> None:
        content_hash = sha256(content)
        old = previous_files.get(page.filename, {})
        unchanged = old.get("hash") == content_hash and old.get("last_updated")
        entry = {
            "title": extract_title(content, page.title),
            "path": page.path,
            "section": page.section.key,
            "original_url": page.url,
            "source_url": source_url,
            "hash": content_hash,
            "last_updated": old["last_updated"] if unchanged else now_iso(),
            "status": status,
        }
        if has_raw:
            entry["raw_fallback"] = True
        entries[page.filename] = entry
        writes[references / page.filename] = content

    for number, page in enumerate(pages, start=1):
        logger.info("Processing %s/%s: %s", number, len(pages), page.path)
        try:
            outcome = process_page(session, product, page)
        except PAGE_ERRORS as error:
            reference = references / page.filename
            if page.filename not in previous_files or not reference.exists():
                logger.error("Failed to process %s: %s", page.path, error)
                failed.append({"path": page.path, "url": page.url, "error": sanitize_error(error)})
                continue
            logger.warning("Serving stale content for %s: %s", page.path, error)
            stale.append({"path": page.path, "url": page.url, "error": sanitize_error(error)})
            raw_copy = raw_dir / page.filename
            if raw_copy.exists():
                writes[raw_copy] = raw_copy.read_text(encoding="utf-8")
            source_url = previous_files[page.filename].get("source_url", page.url)
            record(page, reference.read_text(encoding="utf-8"), source_url, "stale", raw_copy.exists())
            continue
        finally:
            time.sleep(RATE_LIMIT_SECONDS)

        if outcome.kind == "skipped":
            skipped.append({"path": page.path, "url": page.url, "reason": outcome.reason})
            logger.info("Skipped (%s): %s", outcome.reason, page.path)
            continue
        if outcome.kind == "excluded":
            excluded.append({"path": page.path, "url": page.url, "reason": outcome.reason})
            logger.info("Excluded (%s): %s", outcome.reason, page.path)
            continue

        live += 1
        if outcome.raw is not None:
            raw_fallbacks += 1
            writes[raw_dir / page.filename] = outcome.raw
        record(page, outcome.content, outcome.source_url, "live", outcome.raw is not None)

    deletes = [
        references / name
        for name in sorted(previous_files)
        if name not in entries and name not in {MANIFEST_FILE, INDEX_FILE}
    ]
    if raw_dir.is_dir():
        deletes.extend(path for path in sorted(raw_dir.glob("*.md")) if path not in writes)

    manifest = {
        "description": (
            f"{product.name} documentation mirror manifest. "
            "Files live beside this manifest in references/."
        ),
        "source": {
            "base_url": product.base_url,
            "sitemap_urls": list(product.sitemap_urls),
            "llms_txt_url": product.llms_txt_url,
            **product.source_extra,
        },
        "filters": {
            "include": [f"{section.path_prefix}/*" for section in product.sections],
            "exclude_prefixes": list(product.excluded_prefixes),
            "exclude_exact_paths": sorted(product.excluded_paths),
            "exclude_cross_domain": True,
        },
        "files": entries,
        "skipped": skipped,
        "excluded": excluded,
        "fetch_metadata": {
            "total_pages_discovered": len(pages),
            "pages_fetched_successfully": live,
            "pages_stale": len(stale),
            "pages_skipped": len(skipped),
            "pages_excluded": len(excluded),
            "pages_failed": len(failed),
            "failed_pages": failed,
            "stale_pages": stale,
            "raw_fallback_pages": raw_fallbacks,
            "fetch_tool_version": FETCH_TOOL_VERSION,
        },
    }
    unchanged = _projection(previous) == _projection(manifest) and previous.get("last_updated")
    manifest["last_updated"] = previous["last_updated"] if unchanged else now_iso()

    writes[references / INDEX_FILE] = build_index(product, entries, skipped)
    writes[references / MANIFEST_FILE] = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    writes.update(plugin_manifest_writes(root, plugin_version(manifest["last_updated"])))

    problems = check_coverage_guards(
        discovered=len(pages) - len(excluded),
        live=live,
        stale=len(stale),
        skipped=len(skipped),
        previous_file_count=len(previous_files),
        raw_fallbacks=raw_fallbacks,
    )
    if failed:
        listed = ", ".join(item["path"] for item in failed[:10])
        problems.append(f"{len(failed)} page(s) failed: {listed}")
    return Staged(writes=writes, deletes=deletes, manifest=manifest, problems=problems)


def plugin_manifest_writes(root: Path, version: str) -> dict[Path, str]:
    """Return plugin manifests whose ``version`` must move to ``version``."""

    writes: dict[Path, str] = {}
    for relative in PLUGIN_MANIFESTS:
        path = root / relative
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("version") != version:
            data["version"] = version
            writes[path] = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    return writes


def publish(staged: Staged) -> tuple[int, int]:
    """Apply a staged mirror. Returns ``(files_written, files_deleted)``."""

    written = sum(write_text_if_changed(path, content) for path, content in staged.writes.items())
    deleted = 0
    for path in staged.deletes:
        if path.exists():
            logger.info("Removing obsolete file: %s", path.name)
            path.unlink()
            deleted += 1
    for directory in {path.parent for path in staged.deletes}:
        if directory.name == RAW_DIR_NAME and directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
    return written, deleted


def mirror(product: Product, session: requests.Session, *, root: Path = ROOT_DIR) -> dict:
    """Refresh the mirror for ``product``. Raises RuntimeError and writes nothing on failure."""

    previous = load_manifest(product.references_dir(root))
    pages = discover(session, product)
    if not pages:
        raise RuntimeError(f"No {product.name} pages discovered")
    staged = stage(session, product, pages, previous, root=root)
    if staged.problems:
        raise RuntimeError("; ".join(staged.problems))
    written, deleted = publish(staged)
    logger.info("Published: %s files written, %s removed", written, deleted)
    return staged.manifest


# --------------------------------------------------------------------------
# Drift check
# --------------------------------------------------------------------------


def _fetch_from_github(repository: str, ref: str, relative: str) -> bytes | None:
    response = requests.get(
        f"https://raw.githubusercontent.com/{repository}/{ref}/{relative}",
        timeout=REQUEST_TIMEOUT,
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.content


def check_drift(
    product: Product,
    *,
    root: Path = ROOT_DIR,
    ref: str = "main",
    fetch: Callable[[str, str, str], bytes | None] = _fetch_from_github,
) -> list[str]:
    """Compare the shared files with the sibling repositories.

    A coordinated change uses the same branch name in every repository, so a
    sibling's copy of ``ref`` wins when it exists; otherwise its main branch.
    """

    differences: list[str] = []
    for repository in SIBLING_REPOSITORIES:
        if repository == product.repository:
            continue
        sibling_ref = ref
        if ref != "main" and fetch(repository, ref, SHARED_FILES[0]) is None:
            sibling_ref = "main"
        for relative in SHARED_FILES:
            local = root / relative
            if not local.exists():
                differences.append(f"{relative} is missing here")
            elif fetch(repository, sibling_ref, relative) != local.read_bytes():
                differences.append(f"{relative} differs from {repository}@{sibling_ref}")
    return differences


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------


def run(product: Product, argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=f"Mirror the {product.name} documentation into skills/{product.skill}/references/."
    )
    parser.add_argument("--product-name", action="store_true", help="print the product name and exit")
    parser.add_argument(
        "--check-drift",
        action="store_true",
        help="compare the shared files with the sibling repositories and exit",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if args.product_name:
        print(product.name)
        return 0

    if args.check_drift:
        ref = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME") or "main"
        try:
            differences = check_drift(product, ref=ref)
        except requests.RequestException as error:
            logger.error("Drift check could not reach GitHub: %s", sanitize_error(error))
            return 1
        for line in differences:
            logger.error("%s", line)
        if differences:
            logger.error("Update the shared files in all three repositories together.")
            return 1
        logger.info("Shared files match the sibling repositories.")
        return 0

    start = time.monotonic()
    try:
        with requests.Session() as session:
            manifest = mirror(product, session)
    except RuntimeError as error:
        logger.error("%s", error)
        return 1

    metadata = manifest["fetch_metadata"]
    logger.info(
        "Fetch complete in %.1fs: %s live, %s stale, %s skipped, %s excluded, %s raw fallbacks",
        time.monotonic() - start,
        metadata["pages_fetched_successfully"],
        metadata["pages_stale"],
        metadata["pages_skipped"],
        metadata["pages_excluded"],
        metadata["raw_fallback_pages"],
    )
    return 0
