#!/usr/bin/env python3
"""Fetch and clean Claude Code documentation for the claude-code-docs skill."""

from __future__ import annotations

import hashlib
import html
import json
import logging
import random
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests


ROOT_DIR = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT_DIR / "skills" / "claude-code-docs"
REFERENCES_DIR = SKILL_DIR / "references"
RAW_DIR = REFERENCES_DIR / "_raw"
MANIFEST_FILE = "docs_manifest.json"

CLAUDE_CODE_BASE_URL = "https://code.claude.com"
SITEMAP_URLS = [f"{CLAUDE_CODE_BASE_URL}/docs/sitemap.xml"]
# Machine-readable index used as a second discovery source. The former
# docs.anthropic.com sitemap fallback no longer lists any Claude Code page, so
# it could only ever resolve to "no pages discovered".
LLMS_TXT_URL = f"{CLAUDE_CODE_BASE_URL}/docs/llms.txt"

KEEP_PATH_PREFIX = "/docs/en/"
LEGACY_KEEP_PATH_PREFIX = "/en/docs/claude-code/"
EXCLUDED_PREFIXES = (
    "/docs/en/tool-use/",
    "/docs/en/examples/",
    "/docs/en/legacy/",
    "/docs/en/api/",
    "/docs/en/reference/",
)
EXCLUDED_EXACT_PATHS: set[str] = set()

HEADERS = {
    "User-Agent": "claude-code-docs-skill-fetcher/1.0 (+https://code.claude.com/docs)",
    "Accept": "text/plain, text/markdown, application/xml, text/xml, */*",
    "Cache-Control": "no-cache",
}

MAX_RETRIES = 3
REQUEST_TIMEOUT = 30
RATE_LIMIT_SECONDS = 0.2
RETRY_BASE_DELAY_SECONDS = 1
RETRY_MAX_DELAY_SECONDS = 10
MAX_THROTTLE_RETRIES = 5
RAW_FALLBACK_WARNING_THRESHOLD = 0.2

# Coverage guards. A documentation mirror that silently keeps serving old
# content is worse than one that fails loudly, so the run fails when live
# coverage collapses.
MAX_STALE_RATIO = 0.2
MAX_SKIPPED_RATIO = 0.2
MIN_DISCOVERY_RATIO = 0.8
FETCH_TOOL_VERSION = "2.0"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("claude-code-docs")


@dataclass(frozen=True)
class ClaudeCodePage:
    """A Claude Code documentation page discovered from the sitemap."""

    url: str
    path: str
    filename: str
    title: str

    @property
    def markdown_url(self) -> str:
        return f"{self.url.rstrip('/')}.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sanitize_error(error: Exception) -> str:
    """Render an exception without leaking local paths or credentials.

    Error text is recorded in the committed manifest, so a maintainer running
    the fetcher locally must not publish their home directory, their operating
    system username, or credentials embedded in a proxy URL.
    """

    message = f"{type(error).__name__}: {error}"
    message = re.sub(r"//[^/@\s]+:[^/@\s]+@", "//<redacted>@", message)
    message = message.replace(str(ROOT_DIR), "<repo>")
    message = message.replace(str(Path.home()), "<home>")
    message = re.sub(r"/(Users|home)/[^/\s'\"]+", r"/\1/<user>", message)
    return message[:300]


def sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_manifest() -> dict:
    manifest_path = REFERENCES_DIR / MANIFEST_FILE
    if not manifest_path.exists():
        return {"files": {}}

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        logger.warning("Ignoring invalid manifest JSON: %s", error)
        return {"files": {}}

    if "files" not in manifest or not isinstance(manifest["files"], dict):
        manifest["files"] = {}
    return manifest


def write_text_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def fetch_text(
    session: requests.Session, url: str, *, allow_404: bool = False
) -> str | None:
    """Fetch a URL as text, retrying transient failures with backoff."""

    last_error: Exception | None = None
    attempt = 0
    throttle_count = 0
    while attempt < MAX_RETRIES:
        attempt += 1
        try:
            response = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
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
                    f"Rate limited fetching {url} after "
                    f"{MAX_THROTTLE_RETRIES} cooperative retries"
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
            error = requests.HTTPError(
                f"{response.status_code} {response.reason}", response=response
            )
            last_error = error
            _sleep_backoff(url, attempt, error)
            continue

        response.raise_for_status()
        return response.text

    raise RuntimeError(
        f"Failed to fetch {url} after {MAX_RETRIES} attempts: {last_error}"
    )


def _sleep_backoff(url: str, attempt: int, error: Exception) -> None:
    delay = min(
        RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1)), RETRY_MAX_DELAY_SECONDS
    )
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


def _parse_xml(xml_text: str) -> ET.Element:
    """Parse XML defensively against XXE / external-entity attacks."""

    try:
        parser = ET.XMLParser(
            forbid_dtd=True, forbid_entities=True, forbid_external=True
        )
        return ET.fromstring(xml_text, parser=parser)
    except TypeError:
        logger.warning("XMLParser safety parameters unavailable; using default parser")
        return ET.fromstring(xml_text)


def xml_locs(xml_text: str) -> list[str]:
    try:
        root = _parse_xml(xml_text)
    except ET.ParseError as error:
        raise RuntimeError(f"Failed to parse XML: {error}") from error

    locs: list[str] = []
    for element in root.iter():
        if element.tag.endswith("loc") and element.text:
            locs.append(element.text.strip())
    return locs


def normalize_path(path: str) -> str:
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    if path.endswith(".html"):
        path = path.removesuffix(".html")
    if path.endswith(".md"):
        path = path.removesuffix(".md")
    return path


def is_claude_code_doc_url(url: str) -> bool:
    parsed = urlparse(url)
    path = normalize_path(parsed.path)

    if parsed.scheme not in {"http", "https"}:
        return False
    if parsed.netloc not in {"code.claude.com", "docs.anthropic.com"}:
        return False
    if parsed.query:
        return False
    if not (
        path.startswith(KEEP_PATH_PREFIX) or path.startswith(LEGACY_KEEP_PATH_PREFIX)
    ):
        return False
    if path in EXCLUDED_EXACT_PATHS:
        return False
    if any(path.startswith(prefix) for prefix in EXCLUDED_PREFIXES):
        return False
    return True


def _slug_from_path(path: str) -> str:
    if path.startswith(KEEP_PATH_PREFIX):
        return path.removeprefix(KEEP_PATH_PREFIX).strip("/")
    if path.startswith(LEGACY_KEEP_PATH_PREFIX):
        return path.removeprefix(LEGACY_KEEP_PATH_PREFIX).strip("/")
    return path.strip("/")


def path_to_filename(path: str) -> str:
    slug = _slug_from_path(path) or "overview"
    slug = slug.replace("/", "__")
    slug = re.sub(r"[^a-zA-Z0-9_.-]+", "-", slug)
    slug = slug.strip("-._").lower() or "overview"
    return f"{slug}.md"


def title_from_path(path: str) -> str:
    slug = _slug_from_path(path) or "overview"
    return " ".join(part.capitalize() for part in re.split(r"[/_-]+", slug) if part)


def paths_from_sitemaps(session: requests.Session) -> set[str]:
    """Collect documentation paths from the first sitemap that yields URLs."""

    for sitemap_url in SITEMAP_URLS:
        logger.info("Trying sitemap: %s", sitemap_url)
        try:
            sitemap_text = fetch_text(session, sitemap_url, allow_404=True)
        except Exception as error:  # noqa: BLE001 - try the next candidate.
            logger.warning("Failed to fetch sitemap %s: %s", sitemap_url, error)
            continue
        if not sitemap_text:
            continue

        locs = xml_locs(sitemap_text)
        for nested_url in [url for url in locs if url.endswith(".xml")]:
            logger.info("Fetching nested sitemap: %s", nested_url)
            try:
                nested_text = fetch_text(session, nested_url, allow_404=True)
            except Exception as error:  # noqa: BLE001 - skip an unreadable child.
                logger.warning("Failed to fetch %s: %s", nested_url, error)
                continue
            if nested_text:
                locs.extend(xml_locs(nested_text))

        paths = {
            normalize_path(urlparse(url).path)
            for url in locs
            if is_claude_code_doc_url(url)
        }
        if paths:
            logger.info(
                "Discovered %s documentation paths from %s", len(paths), sitemap_url
            )
            return paths

    logger.warning("No documentation paths discovered from any sitemap")
    return set()


def paths_from_llms_txt(session: requests.Session) -> set[str]:
    """Collect documentation paths from the llms.txt index."""

    logger.info("Fetching llms.txt: %s", LLMS_TXT_URL)
    try:
        llms_text = fetch_text(session, LLMS_TXT_URL, allow_404=True)
    except Exception as error:  # noqa: BLE001 - discovery falls back to sitemap.
        logger.warning("Failed to fetch %s: %s", LLMS_TXT_URL, error)
        return set()
    if not llms_text:
        return set()

    paths: set[str] = set()
    for match in re.finditer(
        r"https://code\.claude\.com(/docs/en/[A-Za-z0-9_./-]*)", llms_text
    ):
        path = normalize_path(match.group(1))
        # llms.txt spells the weekly digest index as `whats-new/index`, which is
        # the same page the sitemap lists as `whats-new`.
        path = path.removesuffix("/index") or path
        if is_claude_code_doc_url(f"{CLAUDE_CODE_BASE_URL}{path}"):
            paths.add(path)

    logger.info("Discovered %s documentation paths from llms.txt", len(paths))
    return paths


def pages_from_paths(paths: set[str]) -> list[ClaudeCodePage]:
    pages: list[ClaudeCodePage] = []
    filename_to_path: dict[str, str] = {}
    for path in sorted(paths):
        filename = path_to_filename(path)
        prior_path = filename_to_path.get(filename)
        if prior_path is not None and prior_path != path:
            raise RuntimeError(
                f"Slug collision: {prior_path!r} and {path!r} both map to "
                f"{filename!r}; adjust path_to_filename"
            )
        filename_to_path[filename] = path
        pages.append(
            ClaudeCodePage(
                url=f"{CLAUDE_CODE_BASE_URL}{path}",
                path=path,
                filename=filename,
                title=title_from_path(path),
            )
        )
    return pages


def discover_claude_code_pages(session: requests.Session) -> list[ClaudeCodePage]:
    """Discover pages from the sitemap and llms.txt, then merge both sets."""

    paths = paths_from_sitemaps(session) | paths_from_llms_txt(session)
    pages = pages_from_paths(paths)
    logger.info("Discovered %s Claude Code documentation URLs", len(pages))
    return pages


def preclean_claude_mdx(content: str) -> str:
    content = re.sub(
        r"\A(?:>\s*##\s*Documentation Index\s*\n"
        r">\s*Fetch the complete documentation index at:[^\n]*\n"
        r">\s*Use this file to discover all available pages[^\n]*\n+)",
        "",
        content,
    )
    content = strip_exported_component_blocks(content)

    def outside_fences(text: str) -> str:
        text = re.sub(
            r'<Update\s+label="([^"]+)"\s+description="([^"]+)"\s*>',
            r"### \1 (\2)\n",
            text,
        )
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
        text = convert_html_links(text)
        text = convert_html_text_tags(text)
        return convert_html_tables(text)

    return _apply_outside_fences(content, outside_fences)


def convert_admonition_blocks(content: str) -> str:
    """Unwrap MDX wrapper components without losing the user content they carry.

    Inline single-line admonitions become GitHub-style alert blockquotes.
    Multi-line admonitions have only their opening and closing tags stripped, so
    the inner prose survives the later PascalCase line-drop pass.
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

    title_carrying_tags = ("Tab", "Card", "Accordion", "Expandable")
    for tag in title_carrying_tags:
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
        content = re.sub(
            pattern,
            replacement,
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )
    return content


def convert_html_tables(content: str) -> str:
    def convert_table(match: re.Match[str]) -> str:
        table_html = match.group(0)
        rows: list[list[str]] = []
        for row_match in re.finditer(
            r"<tr\b[^>]*>(.*?)</tr>", table_html, flags=re.IGNORECASE | re.DOTALL
        ):
            row_html = row_match.group(1)
            cells: list[str] = []
            for cell_match in re.finditer(
                r"<t[dh]\b[^>]*>(.*?)</t[dh]>",
                row_html,
                flags=re.IGNORECASE | re.DOTALL,
            ):
                cell = cell_match.group(1)
                cell = re.sub(r"<br\s*/?>", " ", cell, flags=re.IGNORECASE)
                cell = re.sub(r"<[^>]+>", "", cell)
                cell = html.unescape(cell)
                cell = re.sub(r"\s+", " ", cell).strip()
                cell = cell.replace("|", "\\|")
                cells.append(cell)
            if cells:
                rows.append(cells)

        if not rows:
            return ""

        width = max(len(row) for row in rows)
        normalized_rows = [row + [""] * (width - len(row)) for row in rows]
        header = normalized_rows[0]
        markdown = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join("---" for _ in header) + " |",
        ]
        for row in normalized_rows[1:]:
            markdown.append("| " + " | ".join(row) + " |")
        return "\n" + "\n".join(markdown) + "\n"

    return re.sub(
        r"<table\b[^>]*>.*?</table>",
        convert_table,
        content,
        flags=re.IGNORECASE | re.DOTALL,
    )


def strip_inline_markdown_noise(content: str) -> str:
    content = content.replace('{" "}', " ")
    content = content.replace("{' '}", " ")
    content = re.sub(r"\{`([^`]+)`\}", r"`\1`", content)
    return content


def convert_html_links(content: str) -> str:
    def replace_anchor(match: re.Match[str]) -> str:
        href = html.unescape(match.group("href"))
        label = re.sub(r"<[^>]+>", "", match.group("label")).strip()
        label = html.unescape(label)
        if href.startswith("/"):
            href = urljoin(CLAUDE_CODE_BASE_URL, href)
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


def remove_component_tags(content: str) -> str:
    lines = content.splitlines()
    cleaned: list[str] = []
    in_fence = False
    skipping_tag = False
    skipping_script = False

    for line in lines:
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
            if stripped.startswith("</"):
                continue
            if ">" not in stripped:
                skipping_tag = True
            continue

        if re.match(
            r"^</?(div|span|br|section|aside)\b", stripped, flags=re.IGNORECASE
        ):
            if stripped.startswith("</"):
                continue
            if stripped.endswith("/>") or stripped in {"<br>", "<br/>", "<br />"}:
                continue
            if ">" not in stripped:
                skipping_tag = True
                continue
            line = re.sub(
                r"</?(div|span|section|aside)\b[^>]*>", "", line, flags=re.IGNORECASE
            )
            if not line.strip():
                continue

        line = re.sub(r"</?[A-Z][A-Za-z0-9_.-]*\b[^>]*>", "", line)
        line = re.sub(r"<br\s*/?>", "", line, flags=re.IGNORECASE)
        cleaned.append(line)

    return "\n".join(cleaned)


def clean_fence_metadata(content: str) -> str:
    def replace_fence(match: re.Match[str]) -> str:
        fence = match.group("fence")
        lang = match.group("lang") or ""
        metadata = match.group("metadata") or ""
        extras = [
            token
            for token in metadata.split()
            if token and not token.startswith("theme=") and token not in {"terminal"}
        ]
        suffix = f" {' '.join(extras)}" if extras else ""
        return f"{fence}{lang}{suffix}"

    return re.sub(
        r"^\s*(?P<fence>`{3,})(?P<lang>[A-Za-z0-9_-]+)?(?P<metadata>[^\n`]*)$",
        replace_fence,
        content,
        flags=re.MULTILINE,
    )


def normalize_markdown_indentation(content: str) -> str:
    normalized: list[str] = []
    in_fence = False

    for line in content.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            normalized.append(line.lstrip())
            continue
        if not in_fence and re.match(
            r"^\s{2,}(?:!\[|#{1,6}\s|\* |- |\d+\. |\[|`|[A-Za-z0-9].*)",
            line,
        ):
            normalized.append(line.lstrip())
        else:
            normalized.append(line)

    return "\n".join(normalized)


def _split_by_fences(text: str) -> list[tuple[bool, str]]:
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


def _apply_outside_fences(text: str, transform) -> str:
    return "".join(
        chunk if in_fence else transform(chunk)
        for in_fence, chunk in _split_by_fences(text)
    )


def absolutize_links(content: str) -> str:
    """Rewrite root-relative Markdown links to absolute documentation URLs."""

    def replace(match: re.Match[str]) -> str:
        return f"]({CLAUDE_CODE_BASE_URL}{match.group('target')})"

    # Anchored on the link target rather than the label, because labels can
    # themselves contain brackets.
    return re.sub(r"\]\((?P<target>/(?!/)[^)\s]*)\)", replace, content)


def clean_mdx(raw_content: str) -> str:
    content = raw_content.replace("\r\n", "\n")
    content = preclean_claude_mdx(content)

    def outside_fences(text: str) -> str:
        text = re.sub(r"(?ms)^import\s+.*?(?=^\S|\Z)", "", text)
        text = re.sub(r"(?ms)^export\s+.*?(?=^\S|\Z)", "", text)
        text = re.sub(r"(?is)<script\b[^>]*>.*?</script>", "", text)
        text = convert_html_links(text)
        text = convert_keyboard_tags(text)
        text = strip_inline_markdown_noise(text)
        text = absolutize_links(text)
        return text

    content = _apply_outside_fences(content, outside_fences)
    content = remove_component_tags(content)
    content = html.unescape(content)
    content = clean_fence_metadata(content)
    content = normalize_markdown_indentation(content)

    content = re.sub(r"\n{3,}", "\n\n", content)
    content = re.sub(r"[ \t]+\n", "\n", content)
    return content.strip() + "\n"


def content_looks_like_markdown(content: str) -> bool:
    stripped = content.strip()
    if len(stripped) < 50:
        return False
    indicators = (
        "# ",
        "## ",
        "### ",
        "- ",
        "* ",
        "1. ",
        "```",
        "[",
        "|",
        "> ",
    )
    return (
        sum(1 for line in stripped.splitlines() if line.lstrip().startswith(indicators))
        >= 2
    )


def extract_title(content: str, fallback: str) -> str:
    for line in content.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip()
    return fallback


def yaml_quoted(value: str) -> str:
    """Quote a YAML scalar without escaping non-ASCII characters."""

    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def frontmatter_for(page: ClaudeCodePage, *, source_url: str) -> str:
    return (
        "---\n"
        f"title: {yaml_quoted(page.title)}\n"
        f"source: {source_url}\n"
        f"path: {page.path}\n"
        "---\n\n"
    )


def build_index(entries: dict[str, dict], skipped: list[dict]) -> str:
    lines = [
        "# Claude Code Docs Index",
        "",
        "Local mirror of Anthropic Claude Code documentation from https://code.claude.com/docs/en/.",
        "",
        "Invoke this skill with a topic, for example `$claude-code-docs hooks` in Codex or `/claude-code-docs hooks` in Claude Code.",
        "",
        "## Topics",
        "",
    ]

    for filename, metadata in sorted(entries.items(), key=lambda item: item[0]):
        title = metadata.get("title") or filename.removesuffix(".md")
        source = metadata.get("original_url", "")
        lines.append(f"- `{filename.removesuffix('.md')}` - [{title}]({source})")

    if skipped:
        lines.extend(["", "## Skipped Sitemap Pages", ""])
        for item in skipped:
            lines.append(f"- `{item['path']}` - {item['reason']}")

    return "\n".join(lines).strip() + "\n"


def cleanup_old_files(manifest: dict, current_files: set[str]) -> None:
    previous_files = set(manifest.get("files", {}).keys())
    for filename in sorted(previous_files - current_files):
        if filename == MANIFEST_FILE:
            continue
        path = REFERENCES_DIR / filename
        if path.exists():
            logger.info("Removing obsolete file: %s", filename)
            path.unlink()


def save_page(
    page: ClaudeCodePage,
    content: str,
    source_url: str,
    manifest: dict,
    new_files: dict[str, dict],
    current_files: set[str],
    *,
    raw_content: str | None = None,
    status: str = "live",
) -> None:
    content_hash = sha256(content)
    old_entry = manifest.get("files", {}).get(page.filename, {})
    old_hash = old_entry.get("hash")
    last_updated = old_entry.get("last_updated", now_iso())

    if old_hash != content_hash:
        last_updated = now_iso()
        write_text_if_changed(REFERENCES_DIR / page.filename, content)
        logger.info("Updated: %s", page.filename)
    else:
        logger.info("Unchanged: %s", page.filename)

    if raw_content is not None:
        write_text_if_changed(RAW_DIR / page.filename, raw_content)

    new_files[page.filename] = {
        "title": extract_title(content, page.title),
        "path": page.path,
        "original_url": page.url,
        "source_url": source_url,
        "hash": content_hash,
        "last_updated": last_updated,
        "status": status,
    }
    current_files.add(page.filename)


def load_previous_reference(
    page: ClaudeCodePage, manifest: dict
) -> tuple[str, str] | None:
    """Return ``(content, source_url)`` for a previously mirrored page."""

    entry = manifest.get("files", {}).get(page.filename)
    reference_path = REFERENCES_DIR / page.filename
    if not isinstance(entry, dict) or not reference_path.exists():
        return None
    return reference_path.read_text(encoding="utf-8"), entry.get("source_url", page.url)


def check_coverage_guards(
    *,
    discovered: int,
    live: int,
    stale: int,
    skipped: int,
    previous_file_count: int,
) -> list[str]:
    """Return the reasons this run must fail instead of committing."""

    problems: list[str] = []
    if discovered == 0:
        problems.append("Discovery returned no documentation pages")
        return problems

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

    return problems


def fetch_and_save_pages(
    session: requests.Session, pages: list[ClaudeCodePage], manifest: dict
) -> dict:
    new_files: dict[str, dict] = {}
    current_files: set[str] = set()
    skipped: list[dict] = []
    failed: list[dict] = []
    stale: list[dict] = []
    raw_fallback_count = 0
    successful = 0

    for index, page in enumerate(pages, start=1):
        logger.info("Processing %s/%s: %s", index, len(pages), page.path)
        try:
            raw_content = fetch_text(session, page.markdown_url, allow_404=True)
            if raw_content is None:
                skipped.append(
                    {
                        "path": page.path,
                        "url": page.url,
                        "reason": "No .md endpoint",
                    }
                )
                logger.info("Skipped (no markdown endpoint): %s", page.path)
                continue

            cleaned_content = clean_mdx(raw_content)
            page_with_title = ClaudeCodePage(
                page.url,
                page.path,
                page.filename,
                extract_title(cleaned_content, page.title),
            )

            if not content_looks_like_markdown(cleaned_content):
                raw_fallback_count += 1
                logger.warning(
                    "Cleaned content failed markdown sanity check: %s", page.path
                )
                raw_header = (
                    f"# {page_with_title.title}\n\n"
                    f"> Source: {page.url}\n"
                    "> Note: MDX cleaning failed for this page, so this file contains raw source.\n\n"
                )
                content = raw_header + raw_content.strip() + "\n"
                save_page(
                    page_with_title,
                    content,
                    page.markdown_url,
                    manifest,
                    new_files,
                    current_files,
                    raw_content=raw_content,
                )
            else:
                content = (
                    frontmatter_for(page_with_title, source_url=page.url)
                    + cleaned_content
                )
                save_page(
                    page_with_title,
                    content,
                    page.markdown_url,
                    manifest,
                    new_files,
                    current_files,
                )

            successful += 1
            time.sleep(RATE_LIMIT_SECONDS)
        except Exception as error:  # noqa: BLE001 - collect per-page failures.
            previous = load_previous_reference(page, manifest)
            if previous is None:
                logger.error("Failed to process %s: %s", page.path, error)
                failed.append(
                    {"path": page.path, "url": page.url, "error": sanitize_error(error)}
                )
                continue

            previous_content, previous_source = previous
            logger.warning(
                "Serving stale content for %s after fetch failure: %s",
                page.path,
                error,
            )
            stale.append({"path": page.path, "url": page.url, "error": sanitize_error(error)})
            save_page(
                page,
                previous_content,
                previous_source,
                manifest,
                new_files,
                current_files,
                status="stale",
            )

    cleanup_old_files(manifest, current_files)

    index_content = build_index(new_files, skipped)
    write_text_if_changed(REFERENCES_DIR / "INDEX.md", index_content)

    new_manifest = {
        "description": "Claude Code documentation mirror manifest. Files live beside this manifest in references/.",
        "source": {
            "sitemap_urls": SITEMAP_URLS,
            "llms_txt_url": LLMS_TXT_URL,
            "base_url": CLAUDE_CODE_BASE_URL,
        },
        "filters": {
            "include": [f"{KEEP_PATH_PREFIX}*"],
            "exclude_prefixes": list(EXCLUDED_PREFIXES),
            "exclude_exact_paths": sorted(EXCLUDED_EXACT_PATHS),
            "exclude_cross_domain": True,
        },
        "files": new_files,
        "skipped": skipped,
        "fetch_metadata": {
            "total_pages_discovered": len(pages),
            "pages_fetched_successfully": successful,
            "pages_stale": len(stale),
            "pages_skipped": len(skipped),
            "pages_failed": len(failed),
            "failed_pages": failed,
            "stale_pages": stale,
            "raw_fallback_pages": raw_fallback_count,
            "fetch_tool_version": FETCH_TOOL_VERSION,
        },
    }
    if _manifest_projection(manifest) == _manifest_projection(new_manifest):
        new_manifest["last_updated"] = manifest.get("last_updated", now_iso())
    else:
        new_manifest["last_updated"] = now_iso()
    write_text_if_changed(
        REFERENCES_DIR / MANIFEST_FILE,
        json.dumps(new_manifest, indent=2, sort_keys=True) + "\n",
    )

    raw_fallback_ratio = raw_fallback_count / len(pages) if pages else 0
    if raw_fallback_ratio > RAW_FALLBACK_WARNING_THRESHOLD:
        failed.append(
            {
                "path": "*",
                "url": CLAUDE_CODE_BASE_URL,
                "error": (
                    f"Raw fallback triggered for {raw_fallback_count}/{len(pages)} "
                    "pages; cleaner likely regressed"
                ),
            }
        )

    problems = check_coverage_guards(
        discovered=len(pages),
        live=successful,
        stale=len(stale),
        skipped=len(skipped),
        previous_file_count=len(manifest.get("files", {})),
    )
    if failed:
        problems.append(f"{len(failed)} page(s) failed; see {MANIFEST_FILE}")
    if problems:
        raise RuntimeError("; ".join(problems))

    return new_manifest


def _manifest_projection(manifest: dict) -> dict:
    projection = dict(manifest)
    projection.pop("last_updated", None)
    projection.pop("fetch_metadata", None)
    return projection


def main() -> int:
    start = time.monotonic()
    REFERENCES_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest()
    with requests.Session() as session:
        pages = discover_claude_code_pages(session)
        if not pages:
            raise RuntimeError("No Claude Code pages discovered")
        new_manifest = fetch_and_save_pages(session, pages, manifest)

    elapsed = time.monotonic() - start
    metadata = new_manifest["fetch_metadata"]
    logger.info(
        "Fetch complete in %.1fs: %s live, %s stale, %s skipped, %s failed, "
        "%s raw fallbacks",
        elapsed,
        metadata["pages_fetched_successfully"],
        metadata["pages_stale"],
        metadata["pages_skipped"],
        metadata["pages_failed"],
        metadata["raw_fallback_pages"],
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 - clear CLI failure message.
        logger.error("%s", error)
        raise SystemExit(1)
