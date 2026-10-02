#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the static reader and platform ZIPs from the canonical skill."""
import hashlib
import html
import json
import re
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "love-with-clarity"
SITE = ROOT / "site"
VERSION = "0.1.0"


def split_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        _, header, body = text.split("---", 2)
        return yaml.safe_load(header), body.lstrip()
    return {}, text


def slug(text):
    return re.sub(r"[^\w\-]+", "-", text.lower()).strip("-")


def esc(text):
    return html.escape(str(text), quote=True)


def package_files():
    files = {str(path.relative_to(SKILL)): path.read_bytes()
             for path in SKILL.rglob("*") if path.is_file() and not path.name.startswith(".")}
    files["LICENSE.md"] = (ROOT / "LICENSE.md").read_bytes()
    return files


def write_zip(path, files, prefix=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(prefix + name, date_time=(2026, 10, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)


def build_packages():
    files = package_files()
    write_zip(SITE / "downloads" / f"love-with-clarity-codex-{VERSION}.zip", files,
              "love-with-clarity/")
    workbuddy = dict(files)
    workbuddy.pop("agents/openai.yaml", None)
    metadata, body = split_frontmatter(SKILL / "SKILL.md")
    metadata.update({
        "display_name": "看清关系，也照顾自己",
        "display_name_en": "Love With Clarity",
        "description_zh": "整理伴侣的实际行为、自己的需求和边界，选择下一步与自我关爱行动。",
        "description_en": "Reflect on concrete partner behavior, clarify needs and boundaries, and choose a next step with self-care.",
        "version": VERSION,
        "author": "Love With Clarity contributors",
    })
    # The body and references remain identical; only host metadata is adapted.
    workbuddy["SKILL.md"] = ("---\n" + yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False)
                             + "---\n\n" + body).encode("utf-8")
    write_zip(SITE / "downloads" / f"love-with-clarity-workbuddy-{VERSION}.zip", workbuddy)
    checksums = []
    for path in sorted((SITE / "downloads").glob("*.zip")):
        checksums.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (SITE / "downloads" / "SHA256SUMS").write_text("\n".join(checksums) + "\n", encoding="utf-8")


def wrapper(title, body, article=False):
    main_class = "prose" if article else "wrap"
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="从具体行为出发，整理感受与需求，选择自己的下一步。公开指南、20个场景与可导入的AI Skill。">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<title>{esc(title)} · 看清关系，也照顾自己</title><link rel="stylesheet" href="style.css"><script src="app.js" defer></script></head>
<body><a class="skip" href="#main">跳到正文</a><header class="topbar"><div class="wrap header-inner">
<a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">◌</span><span>看清关系，也照顾自己<small>LOVE WITH CLARITY</small></span></a>
<nav class="nav" aria-label="主要导航"><a href="guide.html">指南</a><a href="index.html#scenes">场景</a><a href="index.html#exercises">练习</a><a href="install.html">安装 Skill</a></nav></div></header>
<main id="main" class="{main_class}">{body}</main>
<footer class="footer"><div class="wrap footer-inner"><span>v{VERSION} 草案 · 来源已核对 · 尚待独立专业审阅</span><div class="footer-links"><a href="sources.html">来源与局限</a><a href="privacy.html">隐私</a><a href="validation.html">验证记录</a><a href="license.html">许可</a></div></div></footer></body></html>'''


def download_links():
    return f'''<div class="download-links"><a class="btn" href="downloads/love-with-clarity-workbuddy-{VERSION}.zip" download>下载 WorkBuddy 包</a><a class="btn secondary" href="downloads/love-with-clarity-codex-{VERSION}.zip" download>下载 Codex 包</a></div>'''


def exercise_panel(key, title, description, labels, extra="", hidden=False):
    fields = "".join(f'''<label class="field" for="{key}-{i}">{esc(label)}<textarea id="{key}-{i}" data-label="{esc(label)}" autocomplete="off" spellcheck="false" placeholder="只写你愿意整理的部分"></textarea></label>'''
                     for i, label in enumerate(labels))
    return f'''<section id="exercise-{key}" class="practice-panel" role="tabpanel" aria-labelledby="tab-{key}" {"hidden" if hidden else ""}>
<h3>{esc(title)}</h3><p>{esc(description)}</p>{extra}<form data-exercise="{key}" data-title="{esc(title)}" autocomplete="off">
<div class="field-grid">{fields}</div><div class="form-actions"><button type="button" class="btn" data-action="preview">生成整理稿</button><button type="button" class="btn secondary" data-action="copy">复制</button><button type="button" class="btn secondary" data-action="download">下载 Markdown</button><button type="button" class="plain-button" data-action="clear">清空本练习</button></div></form>
<p class="status" role="status" aria-live="polite"></p><div class="preview" hidden><label for="report-{key}">你的整理稿</label><textarea id="report-{key}" readonly></textarea></div></section>'''


def main():
    SITE.mkdir(exist_ok=True)
    cards = [(path, *split_frontmatter(path)) for path in sorted((SKILL / "references/scenarios").glob("[0-9]*.md"))]
    if len(cards) != 20:
        raise ValueError("Expected twenty scenario cards")
    index = ["# 20 个场景\n", "选最贴近的一件事即可。卡片是个人反思的实践建议，不是诊断或爱情量表。出现危险时先看 [安全支持](../safety.md)。\n", "| 编号 | 类别 | 场景 |", "| --- | --- | --- |"]
    for path, data, _ in cards:
        index.append(f"| {data['id']} | {data['category']} | [{data['title']}]({path.name}) |")
    index.append("\n研究与机构资料只支持明确注明的背景；各卡的局限见正文及 [来源说明](../sources.md)。\n")
    (SKILL / "references/scenarios/index.md").write_text("\n".join(index), encoding="utf-8")

    pages = {
        SKILL / "references/guide.md": "guide.html",
        SKILL / "references/sources.md": "sources.html",
        SKILL / "references/safety.md": "safety.html",
        SKILL / "references/examples.md": "examples.html",
        ROOT / "docs/install.md": "install.html",
        ROOT / "docs/privacy.md": "privacy.html",
        ROOT / "docs/validation.md": "validation.html",
        ROOT / "docs/evaluation.md": "evaluation.html",
        ROOT / "LICENSE.md": "license.html",
        SKILL / "references/scenarios/index.md": "index.html#scenes",
    }
    for key in ["facts-and-guesses", "needs-and-boundaries", "seven-day-care"]:
        pages[SKILL / f"references/exercises/{key}.md"] = {"facts-and-guesses": "facts.html", "needs-and-boundaries": "needs.html", "seven-day-care": "care.html"}[key]
    for path, data, _ in cards:
        pages[path] = "index.html#scene-" + data["id"].lower()
    pages = {path.resolve(): output for path, output in pages.items()}
    md = MarkdownIt("commonmark", {"html": False}).enable("table")

    def render(text, path, prefix=""):
        tokens = md.parse(text)
        used = {}
        def visit(items):
            for i, token in enumerate(items):
                if token.type == "heading_open":
                    ident = prefix + slug(items[i + 1].content)
                    used[ident] = used.get(ident, 0) + 1
                    token.attrSet("id", ident + (f"-{used[ident]}" if used[ident] > 1 else ""))
                if token.type == "link_open":
                    href = token.attrGet("href") or ""
                    parts = urlsplit(href)
                    if parts.path and not parts.scheme and not parts.netloc:
                        target = (path.parent / unquote(parts.path)).resolve()
                        if target in pages:
                            output = pages[target]
                            token.attrSet("href", output + ("#" + parts.fragment if parts.fragment and "#" not in output else ""))
                        else:
                            raise ValueError(f"Unmapped local reader link: {path}: {href}")
                if token.children:
                    visit(token.children)
        visit(tokens)
        return md.renderer.render(tokens, md.options, {})

    for path, output in pages.items():
        if "#" in output:
            continue
        _, body = split_frontmatter(path)
        title = body.splitlines()[0].lstrip("# ")
        rendered = render(body, path)
        if output == "install.html":
            rendered = download_links() + rendered
        rendered = '<a class="document-back" href="index.html">← 回到阅读首页</a>' + rendered
        (SITE / output).write_text(wrapper(title, rendered, article=True), encoding="utf-8")

    categories = list(dict.fromkeys(data["category"] for _, data, _ in cards))
    filters = "".join(f'<button class="filter" type="button" data-category="{esc(category)}" aria-pressed="{str(category == "全部").lower()}">{esc(category)}</button>' for category in ["全部"] + categories)
    card_html = []
    for path, data, body in cards:
        article = re.sub(r"^# [^\n]+\n", "", body, count=1)
        searchable = " ".join([data["id"], data["title"], data["summary"], *data["tags"], body])
        card_html.append(f'''<details class="scene" id="scene-{data['id'].lower()}" data-category="{esc(data['category'])}" data-search="{esc(searchable)}"><summary><span class="meta">{data['id']} · {esc(data['category'])}</span><h3>{esc(data['title'])}</h3><p>{esc(data['summary'])}</p></summary><div class="scene-body">{render(article, path, data['id'].lower() + '-')}</div></details>''')

    facts = exercise_panel("facts", "把事实与猜测分开", "选一个具体事件。不知道的部分可以留空，不需要解释伴侣的全部内心。", ["我看到或听到的行为", "我的感受和生活影响", "我正在作出的解释", "我还不知道什么", "我需要什么", "下一步最小行动", "何时回顾、看什么"])
    needs = exercise_panel("needs", "表达需求，也保留边界", "仅在安全允许时使用。请求可以协商，边界描述自己可以选择的行动。", ["一件具体发生的事", "它对我的影响", "我需要的是", "我想提出的请求", "如果无法达成，我怎样照顾自己"], hidden=True)
    days = ["写下一个感受和需要", "做一件基本照顾", "联系可信任的人", "恢复一点自己的时间", "练习一句温和的自我表达", "安全允许时表达一个小需求", "回顾并保留一件有帮助的事"]
    extra = '<div class="daily-list"><ol>' + ''.join(f'<li>{esc(day)}</li>' for day in days) + '</ol></div>'
    care = exercise_panel("care", "七天，照顾一点自己的生活", "每天选一个能做到的小行动，可换顺序或跳过。七天不是疗效期限。", ["今天选择的行动", "我能做到的最小版本", "做完后的体验，或未完成的原因", "需要调整的地方", "下次想保留什么"], extra=extra, hidden=True)
    body = f'''<section class="hero"><div><span class="eyebrow">从一件具体的事开始</span><h1>看清关系，<br>也照顾自己。</h1><p>当你不确定自己是否被在乎，先把发生的事、心里的担心和真正的需要分开，再选择下一步。</p><div class="actions"><a class="btn" href="#scenes">找到我的场景 ↗</a><a class="btn secondary" href="guide.html">先读公开指南</a></div><p class="tiny">20 个场景 · 3 份练习 · 可导入 Codex / WorkBuddy</p></div>
<aside class="sample" aria-label="一个虚构事件的整理示例"><span class="label">一个虚构事件</span><blockquote>“我们约好的见面取消了，<br>之后也没有新的安排。”</blockquote><div class="sample-row"><b>事实</b><span>约定取消，尚未重新安排。</span></div><div class="sample-row"><b>未知</b><span>原因，以及是否愿意一起调整。</span></div><div class="sample-row"><b>需要</b><span>可靠的安排，也保留自己的时间。</span></div><div class="sample-row"><b>行动</b><span>安全允许时澄清一次，再看实际回应。</span></div></aside></section>
<section class="intro-strip" aria-label="怎样使用"><div><span class="number">01</span><b>看具体行为</b><p>分开事实、感受与猜测，保留未知。</p></div><div><span class="number">02</span><b>说清自己的需要</b><p>找到可调整的请求与个人边界。</p></div><div><span class="number">03</span><b>选一个小行动</b><p>决定由你作出，也给自己现实支持。</p></div></section>
<section class="section" id="scenes"><div class="section-head"><div><h2>哪件事，让你放不下？</h2><p>选最贴近的一张卡，展开看看。它们帮助反思，不给爱情打分。</p></div><a class="text-link" href="safety.html">需要安全支持 ↗</a></div><div class="search-box"><label for="scenario-search">找场景</label><input id="scenario-search" type="search" placeholder="例如：不回消息、道歉、朋友、拒绝" autocomplete="off"></div><div class="filters" aria-label="按类别筛选">{filters}</div><div class="results-line"><span id="result-count" role="status" aria-live="polite">找到 20 个场景</span><button id="reset-filters" type="button" class="plain-button">清除筛选</button></div><div class="scene-grid">{''.join(card_html)}</div><p id="empty-results" class="empty" hidden>没有找到对应场景，试试更简短的词，或清除筛选。</p></section>
<section class="section practice-section" id="exercises"><div class="section-head"><div><h2>留一点时间，整理自己。</h2><p>只写愿意处理的部分。填写不上传；导出与复制由你决定。</p></div><button id="clear-all" type="button" class="plain-button">清空全部填写</button></div><div class="practice-layout"><div><div class="tabs" role="tablist" aria-label="选择练习"><button id="tab-facts" class="tab" role="tab" type="button" data-panel="exercise-facts" aria-controls="exercise-facts" aria-selected="true"><b>事实与猜测</b><span>把一个事件拆开看</span></button><button id="tab-needs" class="tab" role="tab" type="button" data-panel="exercise-needs" aria-controls="exercise-needs" aria-selected="false" tabindex="-1"><b>需求与边界</b><span>找到能说出口的话</span></button><button id="tab-care" class="tab" role="tab" type="button" data-panel="exercise-care" aria-controls="exercise-care" aria-selected="false" tabindex="-1"><b>七天自我关爱</b><span>恢复一点自己的生活</span></button></div><p class="practice-tip">有威胁、强迫或暴力时，请先关注安全。<a href="safety.html">查看支持入口</a><br>想用纸笔？<a href="facts.html">事实表</a> · <a href="needs.html">需求表</a> · <a href="care.html">自我关爱表</a></p></div><div>{facts}{needs}{care}</div></div></section>
<section class="section"><div class="install-band"><div><h2>把这套方法，带进你的 AI 对话。</h2><p>Skill 会根据问题读取相关场景，帮助整理实际行为、需求和可选行动。安装前可查看说明与虚构演示。</p></div><div class="actions"><a class="btn" href="install.html">安装 Skill ↗</a><a class="text-link" href="examples.html">看五个演示</a></div></div></section><aside class="safety-note"><p>本版为 AI 协助起草的草案，来源已核对，尚待独立专业审阅。场景与练习不是诊断、治疗或个人风险评估。</p><a class="text-link" href="sources.html">了解依据与局限 ↗</a></aside>'''
    (SITE / "index.html").write_text(wrapper("阅读与练习", body), encoding="utf-8")
    build_packages()
    print(json.dumps({"version": VERSION, "scenarios": len(cards), "reader_pages": len(list(SITE.glob('*.html'))), "packages": 2}, ensure_ascii=False))


if __name__ == "__main__":
    main()
