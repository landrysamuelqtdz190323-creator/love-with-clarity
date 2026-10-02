#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check cross-file integrity and actual distributable contents, not model quality."""
import hashlib
import json
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/love-with-clarity"
SITE = ROOT / "site"
VERSION = "0.1.0"
MD = MarkdownIt("commonmark", {"html": False}).enable("table")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def parse_skill(text):
    require(text.startswith("---\n"), "Missing frontmatter")
    _, header, body = text.split("---", 2)
    return yaml.safe_load(header), body.lstrip()


def links_in_markdown(text):
    found = []
    def visit(tokens):
        for token in tokens:
            if token.type in ("link_open", "image"):
                found.append(token.attrGet("href") or token.attrGet("src"))
            if token.children:
                visit(token.children)
    visit(MD.parse(text))
    return found


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.links, self.remote_resources = set(), [], []
        self.duplicates = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        ident = attrs.get("id")
        if ident:
            if ident in self.ids:
                self.duplicates.append(ident)
            self.ids.add(ident)
        if tag in ("a", "link") and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag in ("script", "img", "iframe", "link"):
            value = attrs.get("src") or attrs.get("href") or ""
            if urlsplit(value).scheme in ("http", "https"):
                self.remote_resources.append(value)


def main():
    checked = []
    metadata, _ = parse_skill((SKILL / "SKILL.md").read_text())
    require(metadata["name"] == SKILL.name, "Skill name/folder mismatch")
    require(0 < len(metadata["description"]) <= 1024, "Invalid description")
    require(metadata["metadata"]["version"] == VERSION, "Version mismatch")
    require(not (SKILL / "scripts").exists(), "Runtime scripts entered instruction-only skill")
    interface = yaml.safe_load((SKILL / "agents/openai.yaml").read_text())["interface"]
    require(25 <= len(interface["short_description"]) <= 64, "UI description length")
    require("$" + metadata["name"] in interface["default_prompt"], "Invocation metadata mismatch")
    checked.append("canonical skill metadata and UI metadata")

    cards = sorted((SKILL / "references/scenarios").glob("[0-9]*.md"))
    require(len(cards) == 20, "Wrong number of scenarios")
    ids = set()
    sources = set(re.findall(r"^## ([A-Z0-9]+)$", (SKILL / "references/sources.md").read_text(), re.M))
    for path in cards:
        data, body = parse_skill(path.read_text())
        require(data["id"] not in ids, "Duplicate scenario ID")
        ids.add(data["id"])
        require(set(data["sources"]) <= sources, f"Missing source ID in {path.name}")
        require(data["title"] in body, f"Title mismatch in {path.name}")
        require(path.name in (path.parent / "index.md").read_text(), "Scenario absent from index")
    checked.append("twenty scenarios, unique IDs, index and source associations")

    for path in list(SKILL.rglob("*.md")) + list((ROOT / "docs").glob("*.md")) + [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "LICENSE.md"]:
        text = path.read_text()
        require("/Users/chenjianhong" not in text and "/Volumes/" not in text, "Personal machine path in deliverable")
        for href in links_in_markdown(text):
            parts = urlsplit(href)
            if parts.path and not parts.scheme and not parts.netloc:
                require((path.parent / unquote(parts.path)).resolve().exists(), f"Broken Markdown link: {path.name}: {href}")
    checked.append("Markdown links and absence of private machine paths")

    original_files = {str(path.relative_to(SKILL)): path.read_bytes() for path in SKILL.rglob("*") if path.is_file() and not path.name.startswith(".")}
    original_files["LICENSE.md"] = (ROOT / "LICENSE.md").read_bytes()
    zip_names = []
    for platform in ("codex", "workbuddy"):
        name = f"love-with-clarity-{platform}-{VERSION}.zip"
        zip_names.append(name)
        with zipfile.ZipFile(SITE / "downloads" / name) as archive:
            require(archive.testzip() is None, f"Corrupt ZIP: {platform}")
            require(not any(Path(p).is_absolute() or ".." in Path(p).parts for p in archive.namelist()), "Unsafe archive path")
            prefix = "love-with-clarity/" if platform == "codex" else ""
            expected = set(prefix + p for p in original_files if not (platform == "workbuddy" and p == "agents/openai.yaml"))
            require(set(archive.namelist()) == expected, f"Missing or extra package resources: {platform}")
            for path, data in original_files.items():
                if platform == "workbuddy" and path == "agents/openai.yaml":
                    continue
                bundled = archive.read(prefix + path)
                if platform == "workbuddy" and path == "SKILL.md":
                    wb_meta, wb_body = parse_skill(bundled.decode())
                    require(wb_body == parse_skill(data.decode())[1], "Platform instruction body drift")
                    for field in ("description", "description_zh", "description_en", "version", "author"):
                        require(isinstance(wb_meta.get(field), str) and wb_meta[field], f"Missing WorkBuddy field: {field}")
                    require(wb_meta["version"] == VERSION, "WorkBuddy version mismatch")
                else:
                    require(bundled == data, f"Package content drift: {platform}/{path}")
    sums = (SITE / "downloads/SHA256SUMS").read_text()
    for name in zip_names:
        require(f"{hashlib.sha256((SITE / 'downloads' / name).read_bytes()).hexdigest()}  {name}" in sums, "Checksum mismatch")
    checked.append("two ZIPs, complete references, WorkBuddy fields, shared body and checksums")

    pages = {path.resolve(): Page(path.read_text()) for path in SITE.glob("*.html")}
    require(len(pages) >= 10, "Missing reader pages")
    for path, page in pages.items():
        require(not page.duplicates, f"Duplicate HTML IDs: {path.name}: {page.duplicates}")
        require(not page.remote_resources, f"Remote resources in local reader: {path.name}")
        for href in page.links:
            parts = urlsplit(href)
            if parts.scheme or parts.netloc:
                continue
            target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            require(target.exists(), f"Broken HTML target: {path.name}: {href}")
            if parts.fragment:
                require(target in pages and unquote(parts.fragment) in pages[target].ids,
                        f"Broken HTML anchor: {path.name}: {href}")
    checked.append("reader pages, HTML anchors and local assets")
    print(json.dumps({"status": "passed", "checks": checked, "scenarios": len(cards), "pages": len(pages), "note": "File integrity checks do not establish host execution or model behavior."}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
