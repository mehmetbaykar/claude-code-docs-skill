"""Checks that the skill, its plugin manifests, and the mirrored pages agree.

This file is identical in all three docs-skill repositories. CI runs it on
every change and again after each refresh, before anything is published.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import docs_mirror as dm
import fetch_docs


ROOT = Path(__file__).resolve().parents[1]
PRODUCT = fetch_docs.PRODUCT
SKILL_DIR = ROOT / "skills" / PRODUCT.skill
REFERENCES = SKILL_DIR / "references"

# The Agent Skills specification (https://agentskills.io/specification).
# claude.ai uploads and the Skills API reject any other frontmatter key.
AGENT_SKILLS_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
AGENT_PLUGINS_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
AGENT_PLUGINS_FIELDS = {
    "$schema",
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "extensions",
}


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    """Parse the YAML subset SKILL.md uses: scalars, folded blocks, one-level maps."""

    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    assert match, "SKILL.md must start with YAML frontmatter"
    fields: dict[str, object] = {}
    key = ""
    for line in match.group(1).splitlines():
        top = re.match(r"^([A-Za-z][\w-]*):[ \t]*(.*)$", line)
        if top:
            key, value = top.group(1), top.group(2).strip()
            if value == "":
                fields[key] = {}
            elif value in {">", ">-", "|", "|-"}:
                fields[key] = ""
            else:
                fields[key] = value.strip('"')
            continue
        assert key and line.startswith("  "), f"Unexpected frontmatter line: {line!r}"
        current = fields[key]
        if isinstance(current, dict):
            entry = re.match(r"^\s+([\w-]+):\s*(.+)$", line)
            assert entry, f"Unexpected map entry: {line!r}"
            current[entry.group(1)] = entry.group(2).strip().strip('"')
        else:
            fields[key] = f"{current} {line.strip()}".strip()
    return fields, text[match.end() :]


SKILL_TEXT = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
FRONTMATTER, BODY = parse_frontmatter(SKILL_TEXT)


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


# SKILL.md -------------------------------------------------------------------


def test_skill_frontmatter_uses_only_agent_skills_fields() -> None:
    assert set(FRONTMATTER) <= AGENT_SKILLS_FIELDS


def test_skill_name_matches_its_directory_and_the_spec() -> None:
    name = FRONTMATTER["name"]
    assert name == SKILL_DIR.name == PRODUCT.skill
    assert len(name) <= 64
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)


def test_skill_description_fits_the_spec_and_leads_with_the_product() -> None:
    description = FRONTMATTER["description"]
    assert isinstance(description, str)
    assert 1 <= len(description) <= 1024
    # Hosts shorten descriptions when many skills are installed, so the
    # product and the job must come first.
    assert description.startswith("Answers questions about")
    assert PRODUCT.name in description[:80]


def test_optional_skill_fields_fit_the_spec() -> None:
    assert len(str(FRONTMATTER.get("compatibility", ""))) <= 500
    metadata = FRONTMATTER.get("metadata", {})
    assert isinstance(metadata, dict)
    assert all(isinstance(value, str) for value in metadata.values())


def test_skill_body_stays_small() -> None:
    assert len(BODY.splitlines()) <= 500


def test_skill_points_only_at_files_that_exist() -> None:
    mentioned = set(re.findall(r"`(references/[\w.-]+\.(?:md|json))`", BODY))
    assert mentioned, "SKILL.md should name the reference files it relies on"
    for relative in sorted(mentioned):
        assert (SKILL_DIR / relative).exists(), relative


def test_codex_metadata_names_the_skill() -> None:
    text = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
    for key in ("display_name:", "short_description:", "default_prompt:"):
        assert key in text
    assert re.search(r"allow_implicit_invocation:\s*true", text)
    assert f"${PRODUCT.skill}" in text


# Plugin manifests -----------------------------------------------------------


def test_plugin_manifests_agree() -> None:
    portable = load("plugin.json")
    claude = load(".claude-plugin/plugin.json")
    cursor = load(".cursor-plugin/plugin.json")

    assert portable["$schema"] == AGENT_PLUGINS_SCHEMA
    assert set(portable) <= AGENT_PLUGINS_FIELDS
    assert re.fullmatch(r"(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", portable["name"])
    # Claude Code reserves these prefixes for Anthropic's own plugins.
    assert not portable["name"].startswith(("claude-", "anthropic-", "anthropics-", "cc-plugin-"))
    for manifest in (claude, cursor):
        for key in ("name", "version", "description"):
            assert manifest[key] == portable[key], key


@pytest.mark.parametrize("relative", [".claude-plugin/marketplace.json", ".cursor-plugin/marketplace.json"])
def test_marketplaces_list_this_repository_as_its_only_plugin(relative: str) -> None:
    marketplace = load(relative)
    portable = load("plugin.json")
    assert marketplace["name"] == PRODUCT.repository.split("/")[1]
    assert marketplace["owner"]["name"]
    assert marketplace["plugins"] == [
        {"name": portable["name"], "source": "./", "description": portable["description"]}
    ]


def test_plugin_version_tracks_the_mirror() -> None:
    manifest = load(f"skills/{PRODUCT.skill}/references/{dm.MANIFEST_FILE}")
    assert load("plugin.json")["version"] == dm.plugin_version(manifest["last_updated"])


# Mirrored references --------------------------------------------------------


def test_manifest_index_and_reference_files_agree() -> None:
    manifest = json.loads((REFERENCES / dm.MANIFEST_FILE).read_text(encoding="utf-8"))
    files: dict[str, dict] = manifest["files"]
    on_disk = {path.name for path in REFERENCES.glob("*.md")} - {dm.INDEX_FILE}
    assert on_disk == set(files)

    index = (REFERENCES / dm.INDEX_FILE).read_text(encoding="utf-8")
    for name, entry in files.items():
        head = (REFERENCES / name).read_text(encoding="utf-8")[:1000]
        assert head.startswith('---\ntitle: "'), name
        assert f"\nsource: {entry['original_url']}\n" in head, name
        assert f"- `{name.removesuffix('.md')}` - " in index, name

    raw_dir = REFERENCES / dm.RAW_DIR_NAME
    raw = {path.name for path in raw_dir.glob("*.md")} if raw_dir.is_dir() else set()
    assert raw == {name for name, entry in files.items() if entry.get("raw_fallback")}
