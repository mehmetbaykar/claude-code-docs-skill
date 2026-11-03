"""Offline tests for the shared docs_mirror engine.

This file is identical in all three docs-skill repositories and exercises the
engine through a synthetic product. Product behavior is tested in
test_fetch_docs.py.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import requests

import docs_mirror as dm


BASE = "https://docs.example.com"


def legacy_to_docs(path: str) -> str:
    if path == "/old" or path.startswith("/old/"):
        return "/docs" + path.removeprefix("/old")
    return path


DOCS = dm.Section(
    key="docs",
    label="Documentation",
    path_prefix="/docs",
    fetch="markdown",
    mdx=True,
    root_filename="example",
)
GUIDES = dm.Section(
    key="guides",
    label="Guides",
    path_prefix="/guides",
    fetch="html",
    keep_prefix=True,
    html_selector="main#main",
)
PRODUCT = dm.Product(
    name="Example",
    skill="example-docs",
    repository="example/example-docs-skill",
    docs_url=f"{BASE}/docs",
    base_url=BASE,
    sitemap_urls=(f"{BASE}/sitemap.xml",),
    llms_txt_url=f"{BASE}/llms.txt",
    sections=(DOCS, GUIDES),
    alternate_hosts=("old.example.com",),
    excluded_prefixes=("/docs/enterprise/",),
    excluded_paths=("/docs/videos",),
    map_path=legacy_to_docs,
)


class FakeResponse:
    def __init__(self, status: int = 200, text: str = "", headers: dict | None = None):
        self.status_code = status
        self.text = text
        self.content = text.encode("utf-8")
        self.headers = headers or {}
        self.reason = "Fake"

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Fake", response=self)


class FakeSession:
    """Serve canned responses; unknown URLs return 404."""

    def __init__(self, routes: dict[str, object]):
        self.routes = routes
        self.calls: list[str] = []

    def get(self, url: str, headers: dict | None = None, timeout: float | None = None):
        self.calls.append(url)
        route = self.routes.get(url)
        if route is None:
            return FakeResponse(404)
        if isinstance(route, Exception):
            raise route
        if isinstance(route, list):
            return route.pop(0)
        if isinstance(route, FakeResponse):
            return route
        return FakeResponse(200, str(route))


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(dm.time, "sleep", lambda seconds: None)


def sitemap(*paths: str) -> str:
    locs = "".join(f"<url><loc>{BASE}{path}</loc></url>" for path in paths)
    return f'<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{locs}</urlset>'


def page_markdown(title: str, body: str = "Body text that is long enough to count as real content.") -> str:
    return f"# {title}\n\n{body}\n\n## Details\n\n- one\n- two\n"


GUIDE_HTML = """<html><body><nav>Site nav</nav><main id="main">
<h1>Ship faster</h1><p>Read the <a href="/docs/hooks">hooks guide</a> first.</p>
<script>track()</script><nav>In-page nav</nav>
<h2>Steps</h2><ul><li>Plan the change carefully before you start</li><li>Review the diff</li></ul>
<p>Enough prose to keep the converted page above the minimum length threshold.</p>
</main></body></html>"""


def site(**pages: str) -> dict[str, object]:
    """Build routes for a tiny site: ``hooks="..."`` serves /docs/hooks.md."""

    routes: dict[str, object] = {
        f"{BASE}/sitemap.xml": sitemap(*(f"/docs/{name}" for name in pages)),
        f"{BASE}/llms.txt": "",
    }
    for name, content in pages.items():
        routes[f"{BASE}/docs/{name}.md"] = content
    return routes


def run_mirror(tmp_path: Path, routes: dict[str, object], product: dm.Product = PRODUCT) -> dict:
    return dm.mirror(product, FakeSession(routes), root=tmp_path)


def references(tmp_path: Path) -> Path:
    return PRODUCT.references_dir(tmp_path)


# HTTP -----------------------------------------------------------------------


def test_request_retries_server_errors_then_succeeds() -> None:
    session = FakeSession({f"{BASE}/a": [FakeResponse(503), FakeResponse(200, "ok")]})
    response = dm.request(session, f"{BASE}/a", headers={})
    assert response is not None and response.text == "ok"
    assert len(session.calls) == 2


def test_request_returns_none_on_an_allowed_404() -> None:
    assert dm.request(FakeSession({}), f"{BASE}/missing", headers={}, allow_404=True) is None


def test_request_raises_on_a_disallowed_404() -> None:
    with pytest.raises(requests.HTTPError):
        dm.request(FakeSession({}), f"{BASE}/missing", headers={})


def test_request_honours_rate_limits_without_spending_attempts() -> None:
    throttled = [FakeResponse(429, headers={"Retry-After": "1"}) for _ in range(4)]
    session = FakeSession({f"{BASE}/a": [*throttled, FakeResponse(200, "ok")]})
    assert dm.request(session, f"{BASE}/a", headers={}).text == "ok"


def test_request_gives_up_after_max_retries() -> None:
    session = FakeSession({f"{BASE}/a": requests.ConnectionError("down")})
    with pytest.raises(RuntimeError, match="after 3 attempts"):
        dm.request(session, f"{BASE}/a", headers={})


def test_parse_xml_refuses_dtds() -> None:
    with pytest.raises(RuntimeError, match="DTD"):
        dm.parse_xml('<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "b">]><x>&a;</x>')


# Discovery ------------------------------------------------------------------


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (f"{BASE}/docs/hooks", "/docs/hooks"),
        (f"{BASE}/docs/hooks.md", "/docs/hooks"),
        (f"{BASE}/docs/hooks/", "/docs/hooks"),
        (f"{BASE}/docs/whats-new/index", "/docs/whats-new"),
        (f"{BASE}/docs", "/docs"),
        (f"{BASE}/guides/ship-faster", "/guides/ship-faster"),
        ("https://old.example.com/old/prompting.md", "/docs/prompting"),
        (f"{BASE}/docs/enterprise/admin", None),
        (f"{BASE}/docs/videos", None),
        (f"{BASE}/docs/hooks?theme=dark", None),
        (f"{BASE}/docs/llms-full.txt", None),
        (f"{BASE}/pricing", None),
        (f"{BASE}/guides", None),
        ("https://elsewhere.example.org/docs/hooks", None),
        ("ftp://docs.example.com/docs/hooks", None),
    ],
)
def test_page_path_keeps_only_mirrored_pages(url: str, expected: str | None) -> None:
    assert dm.page_path(PRODUCT, url) == expected


def test_page_path_can_strip_query_variants() -> None:
    assert dm.page_path(PRODUCT, f"{BASE}/docs/commands.md?surface=cli", strip_query=True) == "/docs/commands"


@pytest.mark.parametrize(
    ("section", "path", "expected"),
    [
        (DOCS, "/docs/hooks", "hooks.md"),
        (DOCS, "/docs/agent/Overview", "agent__overview.md"),
        (DOCS, "/docs", "example.md"),
        (GUIDES, "/guides/ship-faster", "guides__ship-faster.md"),
    ],
)
def test_filename_for(section: dm.Section, path: str, expected: str) -> None:
    assert dm.filename_for(section, path) == expected


def test_pages_from_paths_detects_slug_collisions() -> None:
    with pytest.raises(RuntimeError, match="Slug collision"):
        dm.pages_from_paths(PRODUCT, {"/docs/cli/features", "/docs/cli__features"})


def test_pages_are_sorted_and_absolute() -> None:
    pages = dm.pages_from_paths(PRODUCT, {"/docs/rules", "/docs/hooks"})
    assert [page.path for page in pages] == ["/docs/hooks", "/docs/rules"]
    assert pages[0].url == f"{BASE}/docs/hooks"
    assert pages[0].title == "Hooks"


def test_discover_merges_nested_sitemaps_and_llms_txt() -> None:
    index = (
        '<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"<sitemap><loc>{BASE}/sitemap-0.xml</loc></sitemap></sitemapindex>"
    )
    routes = {
        f"{BASE}/sitemap.xml": index,
        f"{BASE}/sitemap-0.xml": sitemap("/docs/hooks", "/docs/hooks?surface=cli", "/blog/post"),
        f"{BASE}/llms.txt": (
            f"- [Commands]({BASE}/docs/commands.md?surface=cli)\n"
            f"- [Commands]({BASE}/docs/commands.md?surface=ide)\n"
            "- [Legacy](https://old.example.com/old/prompting.md)\n"
            f"- [Index]({BASE}/llms-full.txt)\n"
        ),
    }
    pages = dm.discover(FakeSession(routes), PRODUCT)
    assert [page.path for page in pages] == ["/docs/commands", "/docs/hooks", "/docs/prompting"]


# Cleaning -------------------------------------------------------------------


RESOLVE = dm.link_resolver(PRODUCT)


def clean(raw: str) -> str:
    return dm.finish_markdown(dm.clean_mdx(raw, RESOLVE))


def test_absolutize_links_maps_legacy_paths_and_keeps_fragments() -> None:
    content = "See [config](/docs/config#auto) and [old](/old/rules)."
    rewritten = dm.absolutize_links(content, RESOLVE)
    assert f"({BASE}/docs/config#auto)" in rewritten
    assert f"({BASE}/docs/rules)" in rewritten


def test_absolutize_links_handles_labels_containing_brackets() -> None:
    rewritten = dm.absolutize_links("[`[auto_review].policy`](/docs/config#policy)", RESOLVE)
    assert f"({BASE}/docs/config#policy)" in rewritten


def test_absolutize_links_leaves_absolute_protocol_relative_and_anchor_links() -> None:
    content = "[a](https://x.example/y) [b](//cdn.example.com/x.png) [c](#top)"
    assert dm.absolutize_links(content, RESOLVE) == content


def test_clean_mdx_preserves_code_fences() -> None:
    cleaned = clean("# Hooks\n\nSee [env](/docs/env).\n\n```bash\ncurl /docs/x\n<Tip>keep</Tip>\n```\n")
    assert f"({BASE}/docs/env)" in cleaned
    assert "curl /docs/x" in cleaned
    assert "<Tip>keep</Tip>" in cleaned


def test_clean_mdx_converts_components_to_markdown() -> None:
    raw = (
        "# Page\n\n"
        "<Tip>Short tip</Tip>\n\n"
        "<Steps>\n"
        '<Step title="Install">\n'
        "Run the installer.\n"
        "</Step>\n"
        "</Steps>\n\n"
        '<Update label="v2.0" description="June 2026">\n'
        "Faster startup.\n"
        "</Update>\n\n"
        "Press <kbd>Ctrl+C</kbd> to stop.\n"
    )
    cleaned = clean(raw)
    assert "> [!TIP] Short tip" in cleaned
    assert "**Install**" in cleaned
    assert "### v2.0 (June 2026)" in cleaned
    assert "`Ctrl+C`" in cleaned
    assert "<" not in cleaned.replace("<!--", "")


def test_clean_mdx_converts_html_tables_and_links() -> None:
    raw = (
        "# Table\n\n"
        "<table><tr><th>Key</th><th>Meaning</th></tr>"
        "<tr><td><code>a|b</code></td><td>Pipe</td></tr></table>\n\n"
        '<a href="/docs/hooks">Hooks</a>\n'
    )
    cleaned = clean(raw)
    assert "| Key | Meaning |" in cleaned
    assert "| `a\\|b` | Pipe |" in cleaned
    assert f"[Hooks]({BASE}/docs/hooks)" in cleaned


def test_clean_mdx_strips_fence_theme_metadata_and_keeps_spacing() -> None:
    cleaned = clean("# Code\n\nRun this:\n\n```bash theme={null} terminal\necho hi\n```\n")
    assert "Run this:\n\n```bash\necho hi\n```" in cleaned


def test_indentation_from_components_is_removed() -> None:
    raw = "**Install**\n\n  Run the installer:\n\n  ```bash\n  npm i\n  ```\n\n  - step a\n    - nested\n"
    assert dm.normalize_markdown_indentation(raw) == (
        "**Install**\n\nRun the installer:\n\n```bash\nnpm i\n```\n\n- step a\n  - nested\n"
    )


def test_nested_lists_keep_their_indentation() -> None:
    raw = "- `pattern`: one of:\n  - a literal\n  - a union\n\n  Continuation paragraph.\n- next\n"
    assert dm.normalize_markdown_indentation(raw) == raw


LANDING = """# Configuration

<OverviewLanding
  title="Configuration"
  description="Set defaults and customize behavior."
  intro="Configuration shapes how the tools behave."
  primaryCta={{
    label: "Explore customization",
    href: "/old/customization",
  }}
  hero={{
    illustration: "configuration",
    alt: "Settings screenshot",
  }}
  sections={[
    {
      title: "Config file",
      description:
        "Control models and tools.",
      pages: [
        {
          title: "Config basics",
          description: 'Create a "config" file.',
          href: "/old/config-basic",
          icon: "settings",
        },
      ],
    },
  ]}
/>
"""


def test_data_components_render_as_markdown() -> None:
    cleaned = clean(LANDING)
    assert "Set defaults and customize behavior." in cleaned
    assert f"[Explore customization]({BASE}/docs/customization)" in cleaned
    assert "## Config file" in cleaned
    assert f'- [Config basics]({BASE}/docs/config-basic): Create a "config" file.' in cleaned
    assert "illustration" not in cleaned
    assert dm.looks_like_markdown(cleaned, strict=True)


def test_glossary_style_components_keep_extra_fields() -> None:
    raw = (
        "# Glossary\n\n<GlossaryTable\n  client:load\n  maxVisibleEntries={100}\n  options={[\n"
        '    { key: "Agent", href: "/docs/agent", appliesTo: "CLI, IDE", description: "The agent." },\n'
        "  ]}\n/>\n"
    )
    assert f"- [Agent]({BASE}/docs/agent): The agent. (Applies to: CLI, IDE)" in clean(raw)


def test_inline_code_keeps_angle_bracket_placeholders() -> None:
    raw = (
        "# Options\n\n"
        "Set `CLAUDE_PLUGIN_OPTION_<KEY>` or run `tool resume <SESSION_ID>`.\n\n"
        "Returns `Array<Item>`; write `<Tip>` literally.\n\n"
        "<Note>Dropped wrapper</Note>\n"
    )
    cleaned = clean(raw)
    assert "`CLAUDE_PLUGIN_OPTION_<KEY>`" in cleaned
    assert "`tool resume <SESSION_ID>`" in cleaned
    assert "`Array<Item>`" in cleaned
    assert "`<Tip>`" in cleaned
    assert "> [!NOTE] Dropped wrapper" in cleaned


def test_text_between_code_spans_is_still_cleaned() -> None:
    cleaned = clean("# Keys\n\n| `a` | `b` | Press <kbd>Enter</kbd> to send, or `Cmd+Enter`. |\n")
    assert "Press `Enter` to send" in cleaned


def test_component_data_keeps_angle_bracket_placeholders() -> None:
    raw = (
        "# Config\n\nIntro line for the configuration page.\n\n<ConfigTable\n  options={[\n"
        '    { key: "hooks.<Event>", type: "array<object>", description: "Hooks for `<Event>`." },\n'
        "  ]}\n/>\n"
    )
    assert "- hooks.<Event>: Hooks for `<Event>`. (Type: array<object>)" in clean(raw)


def test_tree_components_render_as_nested_bullets() -> None:
    raw = (
        "# Layout\n\nIntro line for the layout page.\n\n<FileTree\n  class=\"mt-4\"\n  tree={[\n"
        '    { name: "AGENTS.md", comment: "Repository rules", highlight: true },\n'
        '    { name: "services/", open: true, children: [\n'
        '      { name: "payments/", children: [ { name: "AGENTS.override.md", comment: "Wins" } ] },\n'
        "    ] },\n"
        "  ]}\n/>\n"
    )
    cleaned = clean(raw)
    assert "- AGENTS.md: Repository rules\n- services/\n  - payments/\n    - AGENTS.override.md: Wins" in cleaned
    assert "#" not in cleaned.split("# Layout", 1)[1]
    assert "mt-4" not in cleaned


def test_unreadable_data_components_raise_instead_of_dropping_data() -> None:
    raw = "# Page\n\n<Widget\n  data={[ someVariable ]}\n/>\n\nReal text stays here.\n"
    with pytest.raises(dm.CleaningError, match="Widget"):
        clean(raw)


def test_containers_with_children_are_left_to_the_tag_pass() -> None:
    raw = (
        "# Sandboxing\n\nIntro text for the sandboxing page.\n\n"
        '<Tabs\n  items={["macOS", "Linux"]}\n  label="Platform"\n>\n'
        '<Tab title="macOS">\nSeatbelt runs the command.\n</Tab>\n'
        '<Diagram\n  nodes={["plan", "build"]}\n/>\n'
        "</Tabs>\n"
    )
    cleaned = clean(raw)
    assert "**macOS**" in cleaned
    assert "Seatbelt runs the command." in cleaned
    assert "- plan\n- build" in cleaned


def test_data_values_beyond_strings_are_kept() -> None:
    raw = (
        "# Config\n\nIntro line for the configuration page.\n\n<ConfigTable\n  options={[\n"
        '    { key: `enabled`, type: "boolean", default: false },\n'
        '    { key: "retry", type: "integer", default: 3, values: ["fast", "slow"], open: true },\n'
        "  ]}\n/>\n"
    )
    cleaned = clean(raw)
    assert "- enabled (Type: boolean; Default: false)" in cleaned
    assert "- retry (Type: integer; Default: 3; Values: fast, slow)" in cleaned
    assert "Open" not in cleaned


@pytest.mark.parametrize(
    ("literal", "expected"),
    [
        ("{ a: 1, b: 'x', }", {"a": 1, "b": "x"}),
        ('[ { title: "It\'s", ok: true, none: null }, ]', [{"title": "It's", "ok": True, "none": None}]),
        ("{ label: 'say \"hi\"' }", {"label": 'say "hi"'}),
    ],
)
def test_js_literal_to_python(literal: str, expected: object) -> None:
    assert dm.js_literal_to_python(literal) == expected


def test_js_literal_to_python_rejects_code() -> None:
    with pytest.raises(ValueError):
        dm.js_literal_to_python("{ a: someFunction() }")
    with pytest.raises(ValueError):
        dm.js_literal_to_python("{ a: `hello ${name}` }")


def test_html_to_markdown_keeps_main_content_only() -> None:
    markdown = dm.html_to_markdown(GUIDE_HTML, url=f"{BASE}/guides/ship-faster", selector="main#main")
    assert markdown.lstrip().startswith("# Ship faster")
    assert "[hooks guide](/docs/hooks)" in markdown
    assert "nav" not in markdown.lower()
    assert "track()" not in markdown
    assert "- Plan the change" in markdown


def test_html_to_markdown_takes_the_title_from_outside_the_article() -> None:
    document = (
        "<html><head><title>Guide | Example</title></head><body><header><h1>Best practices</h1></header>"
        '<article id="mainContent"><h2>Plan</h2><p><a href="setup">Set up</a> first.</p></article></body></html>'
    )
    markdown = dm.html_to_markdown(document, url=f"{BASE}/guides/best", selector="article#mainContent")
    assert markdown.startswith("# Best practices\n\n## Plan")
    assert f"[Set up]({BASE}/guides/setup)" in markdown


def test_html_to_markdown_fails_loudly_when_the_layout_changes() -> None:
    with pytest.raises(RuntimeError, match="layout changed"):
        dm.html_to_markdown("<html><body><div>x</div></body></html>", url=BASE, selector="main#main")


def test_looks_like_markdown() -> None:
    assert dm.looks_like_markdown("<!DOCTYPE html><html>" + "x" * 100, strict=False) is False
    assert dm.looks_like_markdown("# Hi\n", strict=False) is False
    prose = "# Title\n\nA real documentation paragraph that is long enough to keep.\n"
    assert dm.looks_like_markdown(prose, strict=False) is True
    assert dm.looks_like_markdown(prose, strict=True) is False
    assert dm.looks_like_markdown(prose + "\n- item\n", strict=True) is True


# Helpers --------------------------------------------------------------------


def test_yaml_quoted_preserves_non_ascii_and_escapes_quotes() -> None:
    assert dm.yaml_quoted("Week 26 · June 22–26") == '"Week 26 · June 22–26"'
    assert dm.yaml_quoted('He said "hi"') == '"He said \\"hi\\""'


def test_frontmatter_quotes_titles_with_colons() -> None:
    page = dm.pages_from_paths(PRODUCT, {"/docs/hooks"})[0]
    frontmatter = dm.frontmatter_for(page, "Hooks: the agent loop")
    assert 'title: "Hooks: the agent loop"' in frontmatter
    assert f"source: {BASE}/docs/hooks" in frontmatter
    assert "path: /docs/hooks" in frontmatter


def test_extract_title_prefers_h1_and_falls_back() -> None:
    assert dm.extract_title("# Hooks\n\nBody\n", "Fallback") == "Hooks"
    assert dm.extract_title("Body\n\n## Section\n", "Fallback") == "Fallback"


def test_plugin_version_is_monotonic_semver() -> None:
    assert dm.plugin_version("2026-11-03T15:34:00+00:00") == "2026.1103.1534"
    assert dm.plugin_version("2027-01-02T00:05:00+00:00") == "2027.102.5"
    assert dm.plugin_version("2026-01-03T13:00:00+00:00") < dm.plugin_version("2026-11-03T13:00:00+00:00")


def test_sanitize_error_strips_local_paths() -> None:
    error = OSError("[Errno 2] No such file or directory: '/Users/someone/Desktop/repo/x.md'")
    message = dm.sanitize_error(error)
    assert "/Users/someone" not in message
    assert "/Users/<user>" in message
    assert message.startswith("OSError: ")


def test_sanitize_error_redacts_proxy_credentials() -> None:
    message = dm.sanitize_error(requests.ConnectionError("https://alice:hunter2@proxy.example/"))
    assert "hunter2" not in message
    assert "<redacted>@proxy.example" in message


def test_sanitize_error_replaces_the_repository_root() -> None:
    message = dm.sanitize_error(OSError(f"cannot write {dm.ROOT_DIR}/skills/x.md"))
    assert str(dm.ROOT_DIR) not in message
    assert "<repo>" in message


def test_sanitize_error_is_bounded() -> None:
    assert len(dm.sanitize_error(RuntimeError("x" * 5000))) == 300


# Coverage guards ------------------------------------------------------------


def test_guards_pass_on_a_healthy_run() -> None:
    assert dm.check_coverage_guards(discovered=150, live=149, stale=1, skipped=0, previous_file_count=150) == []


def test_guards_fail_on_empty_discovery() -> None:
    assert dm.check_coverage_guards(discovered=0, live=0, stale=0, skipped=0, previous_file_count=150) == [
        "Discovery returned no documentation pages"
    ]


@pytest.mark.parametrize(
    ("counts", "message"),
    [
        ({"live": 0, "stale": 150, "skipped": 0}, "No page was fetched live"),
        ({"live": 10, "stale": 0, "skipped": 140}, "no usable Markdown"),
        ({"live": 100, "stale": 50, "skipped": 0}, "served stale content"),
    ],
)
def test_guards_fail_when_live_coverage_collapses(counts: dict, message: str) -> None:
    problems = dm.check_coverage_guards(discovered=150, previous_file_count=150, **counts)
    assert any(message in problem for problem in problems)


def test_guards_fail_when_discovery_collapses() -> None:
    problems = dm.check_coverage_guards(discovered=10, live=10, stale=0, skipped=0, previous_file_count=150)
    assert any("refusing to delete references" in problem for problem in problems)


def test_guards_fail_when_cleaning_regresses() -> None:
    problems = dm.check_coverage_guards(
        discovered=100, live=100, stale=0, skipped=0, previous_file_count=100, raw_fallbacks=30
    )
    assert any("cleaner likely regressed" in problem for problem in problems)


# End-to-end runs ------------------------------------------------------------


def snapshot(root: Path) -> dict[str, bytes]:
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()}


def test_a_healthy_run_publishes_pages_index_manifest_and_versions(tmp_path: Path) -> None:
    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / ".claude-plugin" / "plugin.json").write_text('{"name": "example-docs"}\n')
    routes = site(hooks=page_markdown("Hooks"), rules=page_markdown("Rules"))
    routes[f"{BASE}/sitemap.xml"] = sitemap("/docs/hooks", "/docs/rules", "/guides/ship-faster")
    routes[f"{BASE}/guides/ship-faster"] = GUIDE_HTML

    manifest = run_mirror(tmp_path, routes)

    hooks = (references(tmp_path) / "hooks.md").read_text()
    assert hooks.startswith(f'---\ntitle: "Hooks"\nsource: {BASE}/docs/hooks\npath: /docs/hooks\n---\n\n# Hooks')
    index = (references(tmp_path) / "INDEX.md").read_text()
    assert "## Documentation" in index and "## Guides" in index
    assert f"- `guides__ship-faster` - [Ship faster]({BASE}/guides/ship-faster)" in index
    assert "`$example-docs hooks` in Codex" in index
    assert manifest["files"]["hooks.md"]["section"] == "docs"
    assert manifest["files"]["guides__ship-faster.md"]["status"] == "live"
    assert manifest["fetch_metadata"]["pages_fetched_successfully"] == 3
    version = json.loads((tmp_path / ".claude-plugin" / "plugin.json").read_text())["version"]
    assert version == dm.plugin_version(manifest["last_updated"])


def test_an_unchanged_run_writes_nothing(tmp_path: Path) -> None:
    routes = site(hooks=page_markdown("Hooks"))
    first = run_mirror(tmp_path, routes)
    before = snapshot(tmp_path)

    second = run_mirror(tmp_path, routes)

    assert snapshot(tmp_path) == before
    assert second["last_updated"] == first["last_updated"]


def test_a_failed_run_leaves_the_mirror_untouched(tmp_path: Path) -> None:
    run_mirror(tmp_path, site(**{f"page{n}": page_markdown(f"Page {n}") for n in range(10)}))
    before = snapshot(tmp_path)

    with pytest.raises(RuntimeError, match="refusing to delete references"):
        run_mirror(tmp_path, site(page0=page_markdown("Page 0 changed")))

    assert snapshot(tmp_path) == before


def test_a_page_that_fails_without_history_fails_the_run_and_writes_nothing(tmp_path: Path) -> None:
    routes = site(hooks=page_markdown("Hooks"))
    routes[f"{BASE}/sitemap.xml"] = sitemap("/docs/hooks", "/docs/broken")
    routes[f"{BASE}/docs/broken.md"] = FakeResponse(403)

    with pytest.raises(RuntimeError, match="1 page\\(s\\) failed: /docs/broken"):
        run_mirror(tmp_path, routes)

    assert not references(tmp_path).exists()


def test_fetch_errors_serve_stale_content(tmp_path: Path) -> None:
    pages = {f"page{n}": page_markdown(f"Page {n}") for n in range(10)}
    run_mirror(tmp_path, site(**pages))
    previous = (references(tmp_path) / "page3.md").read_text()

    routes = site(**pages)
    routes[f"{BASE}/docs/page3.md"] = requests.ConnectionError("down")
    manifest = run_mirror(tmp_path, routes)

    assert (references(tmp_path) / "page3.md").read_text() == previous
    assert manifest["files"]["page3.md"]["status"] == "stale"
    assert manifest["fetch_metadata"]["pages_stale"] == 1


def test_pages_that_disappear_are_removed(tmp_path: Path) -> None:
    pages = {f"page{n}": page_markdown(f"Page {n}") for n in range(10)}
    run_mirror(tmp_path, site(**pages))
    del pages["page9"]

    manifest = run_mirror(tmp_path, site(**pages))

    assert not (references(tmp_path) / "page9.md").exists()
    assert "page9.md" not in manifest["files"]


def test_raw_fallback_is_kept_then_removed_once_cleaning_recovers(tmp_path: Path) -> None:
    pages = {f"page{n}": page_markdown(f"Page {n}") for n in range(9)}
    pages["landing"] = "# Landing\n\n<Hero\n  title={someVariable}\n/>\n"
    first = run_mirror(tmp_path, site(**pages))

    raw_copy = references(tmp_path) / "_raw" / "landing.md"
    assert raw_copy.exists()
    assert first["files"]["landing.md"]["raw_fallback"] is True
    assert "Cleaning failed" in (references(tmp_path) / "landing.md").read_text()

    pages["landing"] = page_markdown("Landing")
    second = run_mirror(tmp_path, site(**pages))

    assert not raw_copy.exists()
    assert not raw_copy.parent.exists()
    assert "raw_fallback" not in second["files"]["landing.md"]


def test_unreadable_data_components_keep_the_raw_source(tmp_path: Path) -> None:
    pages = {f"page{n}": page_markdown(f"Page {n}") for n in range(9)}
    pages["config"] = page_markdown("Config") + "\n<ConfigTable\n  options={[ { key: someVariable } ]}\n/>\n"

    manifest = run_mirror(tmp_path, site(**pages))

    assert manifest["files"]["config.md"]["raw_fallback"] is True
    assert "someVariable" in (references(tmp_path) / "_raw" / "config.md").read_text()
    assert manifest["fetch_metadata"]["raw_fallback_pages"] == 1


def test_product_hooks_exclude_clean_and_special_fetch(tmp_path: Path) -> None:
    def exclude(page: dm.Page, raw: str) -> str | None:
        return "Not about Example" if "OTHER PRODUCT" in raw else None

    def special(session, product, page) -> tuple[str, str]:
        return "# Changelog\n\n## v1\n\n- Initial release\n", f"{BASE}/feed.xml"

    product = dm.Product(
        **{
            **PRODUCT.__dict__,
            "exclude": exclude,
            "clean": lambda page, content: content.replace("BOILERPLATE\n", ""),
            "special": {"/docs/changelog": special},
        }
    )
    routes = site(
        hooks="BOILERPLATE\n" + page_markdown("Hooks"),
        other=page_markdown("Other", "OTHER PRODUCT content that should not be mirrored."),
    )
    routes[f"{BASE}/sitemap.xml"] = sitemap("/docs/hooks", "/docs/other", "/docs/changelog")

    manifest = dm.mirror(product, FakeSession(routes), root=tmp_path)

    assert "BOILERPLATE" not in (references(tmp_path) / "hooks.md").read_text()
    assert not (references(tmp_path) / "other.md").exists()
    assert manifest["excluded"] == [{"path": "/docs/other", "url": f"{BASE}/docs/other", "reason": "Not about Example"}]
    assert manifest["files"]["changelog.md"]["source_url"] == f"{BASE}/feed.xml"


# Drift check ----------------------------------------------------------------


def test_check_drift_compares_shared_files_with_the_other_repositories(tmp_path: Path) -> None:
    for relative in dm.SHARED_FILES:
        (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / relative).write_bytes(b"shared\n")
    product = dm.Product(**{**PRODUCT.__dict__, "repository": dm.SIBLING_REPOSITORIES[0]})
    requested: list[tuple[str, str]] = []

    def fetch(repository: str, ref: str, relative: str) -> bytes | None:
        requested.append((repository, ref))
        if ref == "feature" and repository != dm.SIBLING_REPOSITORIES[1]:
            return None  # only the second sibling has the feature branch
        if repository == dm.SIBLING_REPOSITORIES[2] and relative == "scripts/docs_mirror.py":
            return b"changed\n"
        return b"shared\n"

    differences = dm.check_drift(product, root=tmp_path, ref="feature", fetch=fetch)

    assert differences == [f"scripts/docs_mirror.py differs from {dm.SIBLING_REPOSITORIES[2]}@main"]
    assert all(repository != dm.SIBLING_REPOSITORIES[0] for repository, _ in requested)
    assert (dm.SIBLING_REPOSITORIES[1], "feature") in requested
