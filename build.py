#!/usr/bin/env python3
"""
自刻的靜態網站產生器（取代 Hugo + PaperMod）。

用法：
    python build.py                 產生網站到 public/
    python build.py serve           產生網站並在 http://localhost:1313 預覽（改檔自動重建、瀏覽器自動重新整理）
    python build.py serve --port 8000
    python build.py serve --lan     讓同一個 Wi-Fi 的手機也能連進來預覽
    python build.py new "文章標題"   在 content/posts/ 建立新文章
    加上 --drafts 會連 draft = true 的文章一起產生；加上 --future 會連未來日期的文章一起產生。

需要的套件：pip install -r requirements.txt
"""
from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
import shutil
import sys
import threading
import time
import tomllib
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from email.utils import format_datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote

from markdown_it import MarkdownIt
from pygments import highlight as pyg_highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content" / "posts"
STATIC = ROOT / "static"
ASSETS = ROOT / "assets"
OUT = ROOT / "public"
CONFIG = ROOT / "site.toml"

TZ = timezone(timedelta(hours=8))

# 開發模式（serve）時注入自動重新整理腳本
LIVE_RELOAD = False
BUILD_ID = 0


# ---------------------------------------------------------------------------
# 工具函式
# ---------------------------------------------------------------------------

def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def urlize(s: str) -> str:
    """模仿 Hugo 的 urlize：小寫、空白轉 '-'、去掉多數標點，保留中文等文字。"""
    s = unicodedata.normalize("NFC", s.strip().lower())
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^\w\-.]", "", s)
    return s


def heading_id(text: str) -> str:
    """產生標題錨點 id（類似 GitHub / goldmark 的規則）。"""
    s = text.strip().lower()
    out = []
    for ch in s:
        if ch.isalnum() or ch in "-_":
            out.append(ch)
        elif ch.isspace():
            out.append("-")
    return "".join(out) or "heading"


TAG_RE = re.compile(r"<[^>]+>")


def strip_tags(s: str) -> str:
    return html.unescape(TAG_RE.sub("", s))


CJK_RE = re.compile(r"[぀-ヿ㐀-䶿一-鿿豈-﫿가-힯]")


def reading_minutes(text: str, wpm: int) -> int:
    cjk = len(CJK_RE.findall(text))
    words = len(CJK_RE.sub(" ", text).split())
    return max(1, math.ceil(cjk / 500 + words / wpm))


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Markdown 轉換
# ---------------------------------------------------------------------------

_formatter = HtmlFormatter(nowrap=True)


def highlight_code(code: str, lang: str, _attrs) -> str:
    lang = (lang or "").strip().split()[0] if lang else ""
    if not lang:
        return ""  # 讓 markdown-it 用預設 <pre><code>
    try:
        lexer = get_lexer_by_name(lang)
    except ClassNotFound:
        return ""
    body = pyg_highlight(code, lexer, _formatter)
    return f'<pre><code class="language-{esc(lang)}">{body}</code></pre>'


def make_md() -> MarkdownIt:
    # Hugo 預設的 goldmark 是 CommonMark + GFM（表格、刪除線、自動連結）
    md = MarkdownIt("commonmark", {"html": False, "linkify": True, "highlight": highlight_code})
    md.enable(["table", "strikethrough", "linkify"])

    def fence(self, tokens, idx, options, env):
        tok = tokens[idx]
        info = tok.info.strip()
        hl = highlight_code(tok.content, info, None)
        if hl:
            return f'<div class="highlight">{hl}</div>\n'
        return f"<pre><code>{esc(tok.content)}</code></pre>\n"

    md.add_render_rule("fence", fence)
    return md


MD = make_md()


@dataclass
class Heading:
    level: int
    id: str
    text: str


def render_markdown(src: str) -> tuple[str, list[Heading]]:
    env: dict = {}
    tokens = MD.parse(src, env)
    headings: list[Heading] = []
    used: dict[str, int] = {}
    for i, tok in enumerate(tokens):
        if tok.type == "heading_open":
            inline = tokens[i + 1]
            text = strip_tags(MD.renderer.render(inline.children or [], MD.options, env))
            base = heading_id(text)
            n = used.get(base, 0)
            used[base] = n + 1
            hid = base if n == 0 else f"{base}-{n}"
            tok.attrSet("id", hid)
            headings.append(Heading(int(tok.tag[1]), hid, text))
    body = MD.renderer.render(tokens, MD.options, env)
    # 標題後加上 # 錨點（滑過標題時顯示）
    body = re.sub(
        r'<h([1-6]) id="([^"]*)">(.*?)</h\1>',
        lambda m: f'<h{m[1]} id="{m[2]}">{m[3]}<a hidden class="anchor" aria-hidden="true" href="#{m[2]}">#</a></h{m[1]}>',
        body,
        flags=re.S,
    )
    return body, headings


def toc_html(headings: list[Heading]) -> str:
    if not headings:
        return ""
    top = min(h.level for h in headings)
    parts = ["<ul>"]
    depth = top
    first = True
    for h in headings:
        if first:
            while depth < h.level:
                parts.append("<li><ul>")
                depth += 1
            first = False
        elif h.level > depth:
            while depth < h.level:
                parts.append("<ul>")
                depth += 1
        else:
            parts.append("</li>")
            while depth > h.level:
                parts.append("</ul></li>")
                depth -= 1
        parts.append(f'<li><a href="#{esc(h.id)}" aria-label="{esc(h.text)}">{esc(h.text)}</a>')
    parts.append("</li>")
    while depth > top:
        parts.append("</ul></li>")
        depth -= 1
    parts.append("</ul>")
    return (
        '<div class="toc"><details><summary accesskey="c" title="(Alt + C)">'
        '<span class="details">目錄</span></summary>'
        f'<div class="inner">{"".join(parts)}</div></details></div>'
    )


# ---------------------------------------------------------------------------
# 內容讀取
# ---------------------------------------------------------------------------

@dataclass
class Post:
    src: Path
    title: str
    date: datetime
    draft: bool
    tags: list[str]
    categories: list[str]
    cover: dict
    slug: str
    body_md: str
    html: str = ""
    headings: list[Heading] = field(default_factory=list)
    text: str = ""
    summary: str = ""
    minutes: int = 1
    description: str = ""

    @property
    def url(self) -> str:
        return f"/posts/{self.slug}/"


def parse_front_matter(raw: str, path: Path) -> tuple[dict, str]:
    raw = raw.lstrip("﻿")
    if raw.startswith("+++"):
        end = raw.find("\n+++", 3)
        if end == -1:
            raise ValueError(f"{path}: front matter 沒有結束的 +++")
        fm = tomllib.loads(raw[3:end])
        body = raw[end + 4:]
        return fm, body.lstrip("\r\n")
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        fm: dict = {}
        for line in raw[3:end].splitlines():
            if ":" in line and not line.strip().startswith("#"):
                k, v = line.split(":", 1)
                fm[k.strip()] = v.split("#")[0].strip().strip("\"'")
        return fm, raw[end + 4:].lstrip("\r\n")
    return {}, raw


def to_datetime(v) -> datetime:
    if isinstance(v, datetime):
        return v if v.tzinfo else v.replace(tzinfo=TZ)
    if hasattr(v, "year"):
        return datetime(v.year, v.month, v.day, tzinfo=TZ)
    if isinstance(v, str) and v:
        d = datetime.fromisoformat(v)
        return d if d.tzinfo else d.replace(tzinfo=TZ)
    return datetime.now(TZ)


def resolve_static(ref: str) -> str:
    """把封面等圖片路徑轉成網址；找不到檔案時嘗試同名不同副檔名。"""
    if not ref or "://" in ref:
        return ref
    rel = ref.lstrip("/")
    if (STATIC / rel).exists():
        return "/" + rel
    stem = Path(rel).with_suffix("")
    for cand in sorted(STATIC.glob(f"{stem}.*")):
        print(f"  ! 找不到 {rel}，改用 {cand.relative_to(STATIC).as_posix()}")
        return "/" + cand.relative_to(STATIC).as_posix()
    print(f"  ! 找不到圖片 {rel}")
    return "/" + rel


def load_posts(cfg: dict, drafts: bool, future: bool) -> list[Post]:
    posts: list[Post] = []
    now = datetime.now(TZ)
    for p in sorted(CONTENT.glob("*.md")):
        fm, body = parse_front_matter(p.read_text(encoding="utf-8"), p)
        post = Post(
            src=p,
            title=str(fm.get("title", p.stem)),
            date=to_datetime(fm.get("date")),
            draft=bool(fm.get("draft", False)),
            tags=[str(t) for t in fm.get("tags", [])],
            categories=[str(c) for c in fm.get("categories", [])],
            cover=dict(fm.get("cover", {})),
            slug=str(fm.get("slug") or urlize(p.stem)),
            body_md=body,
            description=str(fm.get("description", "")),
        )
        if post.draft and not drafts:
            continue
        if post.date > now and not future:
            print(f"  - 略過未來日期文章：{p.name}（{post.date:%Y-%m-%d}）")
            continue
        if post.cover.get("image"):
            post.cover["image"] = resolve_static(post.cover["image"])
        post.html, post.headings = render_markdown(body)
        post.text = re.sub(r"\s+", " ", strip_tags(post.html.replace('href="#', 'x="'))).replace("#", "").strip()
        post.summary = post.description or (post.text[:140] + ("…" if len(post.text) > 140 else ""))
        post.minutes = reading_minutes(post.text, cfg.get("words_per_minute", 213))
        posts.append(post)
    posts.sort(key=lambda x: x.date, reverse=True)
    return posts


# ---------------------------------------------------------------------------
# 圖示
# ---------------------------------------------------------------------------

SVG = {
    "github": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.870a3.370 3.370 0 0 0-.94-2.610c3.140-.35 6.440-1.540 6.440-7A5.440 5.440 0 0 0 20 4.770 5.070 5.070 0 0 0 19.910 1S18.730.65 16 2.480a13.380 13.380 0 0 0-7 0C6.270.65 5.090 1 5.090 1A5.070 5.070 0 0 0 5 4.770a5.440 5.440 0 0 0-1.500 3.780c0 5.420 3.300 6.610 6.440 7A3.370 3.370 0 0 0 9 18.130V22"/></svg>',
    "linkedin": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg>',
    "kaggle": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="currentColor"><path transform="matrix(.527027 0 0 .527027 -30.632288 -22.45559)" d="M105.75 102.968c-.06.238-.298.357-.713.357H97.1c-.477 0-.89-.208-1.248-.625L82.746 86.028l-3.655 3.477v12.93c0 .595-.298.892-.892.892h-6.152c-.595 0-.892-.297-.892-.892V43.5c0-.593.297-.89.892-.89H78.2c.594 0 .892.298.892.89v36.288l15.692-15.870c.416-.415.832-.624 1.248-.624h8.204c.356 0 .593.15.713.445.12.357.09.624-.09.803L88.274 80.588l17.297 21.488c.237.238.297.535.18.892"/></svg>',
    "instagram": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" y1="6.5" x2="17.5" y2="6.5"/></svg>',
    "x": '<svg viewBox="0 0 512 512" fill="currentColor"><path d="M512 62.554V449.446C512 483.97 483.97 512 449.446 512H62.554C28.03 512 0 483.97 0 449.446V62.554C0 28.03 28.029 0 62.554 0H449.446C483.971 0 512 28.03 512 62.554ZM269.951 190.75 182.567 75.216H56L207.216 272.95 63.9 436.783H125.266L235.9 310.383 332.567 436.783H456L298.367 228.367 432.367 75.216H371.033ZM127.633 110H164.101L383.481 400.065H349.5Z"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>',
    "link": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
    "external": '<svg fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" viewBox="0 0 24 24" height="12" width="12"><path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/><path d="M15 3h6v6"/><path d="M10 14L21 3"/></svg>',
}

MOON_SUN = (
    '<svg id="moon" width="24" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'
    '<svg id="sun" width="24" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>'
)


# ---------------------------------------------------------------------------
# 版型
# ---------------------------------------------------------------------------

KATEX = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.css" integrity="sha384-zh0CIslj+VczCZtlzBcjt5ppRcsAmDnRem7ESsYwWwg3m/OaJ2l4x7YBZl9Kxxib" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.js" integrity="sha384-Rma6DA2IPUwhNxmrB/7S3Tno0YY7sFu9WSYMCuulLhIqYSGZ2gKCJWIqhBWqMQfh" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/contrib/auto-render.min.js" integrity="sha384-hCXGrW6PitJEwbkoStFjeJxv+fSOOQKOPbJxSfM6G5sWZjAyWhXiTIIAmQqnlLlh" crossorigin="anonymous"
  onload="renderMathInElement(document.querySelector('.post-content') || document.body, {delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false},{left:'\\\\(',right:'\\\\)',display:false},{left:'\\\\[',right:'\\\\]',display:true}],throwOnError:false});"></script>
"""

LIVE_JS = """<script>
(function(){var id=null;setInterval(function(){fetch('/__build').then(function(r){return r.text()}).then(function(t){if(id===null)id=t;else if(t!==id)location.reload();}).catch(function(){});},1000);})();
</script>"""


class Site:
    def __init__(self, cfg: dict, posts: list[Post]):
        self.cfg = cfg
        self.posts = posts
        self.title = cfg.get("title", "My Site")
        self.base = cfg.get("base_url", "").rstrip("/")
        self.tags = self._group("tags")
        self.categories = self._group("categories")

    def _group(self, attr: str) -> dict[str, tuple[str, list[Post]]]:
        groups: dict[str, tuple[str, list[Post]]] = {}
        for p in self.posts:
            for name in getattr(p, attr):
                slug = urlize(name)
                if slug not in groups:
                    groups[slug] = (name, [])
                groups[slug][1].append(p)
        return dict(sorted(groups.items(), key=lambda kv: kv[1][0].lower()))

    # ---------- 共用區塊 ----------

    def header(self, current: str) -> str:
        items = []
        for m in self.cfg.get("menu", []):
            url = m["url"]
            ext = "://" in url
            active = ' class="active"' if not ext and current.startswith(url) else ""
            attrs = ' target="_blank" rel="noopener"' if ext else ""
            if url == "/search/":
                attrs += ' accesskey="/" title="Search (Alt + /)"'
            items.append(
                f'<li><a href="{esc(url)}"{attrs}><span{active}>{esc(m["name"])}</span>'
                f'{"&nbsp;" + SVG["external"] if ext else ""}</a></li>'
            )
        return f"""<header class="header">
  <nav class="nav">
    <div class="logo">
      <a href="/" accesskey="h" title="{esc(self.title)} (Alt + H)">{esc(self.title)}</a>
      <div class="logo-switches">
        <button id="theme-toggle" accesskey="t" title="切換深淺色 (Alt + T)" aria-label="切換深淺色">{MOON_SUN}</button>
      </div>
    </div>
    <ul id="menu">{"".join(items)}</ul>
  </nav>
</header>"""

    def footer(self) -> str:
        year = datetime.now(TZ).year
        return f"""<footer class="footer">
  <span>&copy; {year} <a href="/">{esc(self.title)}</a></span> ·
  <span>Powered by 自刻的 build.py</span>
</footer>
<a href="#top" aria-label="回到頂端" title="回到頂端 (Alt + G)" class="top-link" id="top-link" accesskey="g">
  <svg viewBox="0 0 12 6" fill="currentColor"><path d="M12 6H0l6-6z"/></svg>
</a>"""

    def page(self, *, title: str, body: str, current: str = "", is_list: bool = True,
             description: str = "", math: bool = False, extra_head: str = "") -> str:
        full_title = self.title if title == self.title else f"{title} | {self.title}"
        return f"""<!DOCTYPE html>
<html lang="{esc(self.cfg.get('language', 'zh-TW'))}">
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description or self.cfg.get('profile', {}).get('subtitle', ''))}">
<link rel="stylesheet" href="/assets/style.css?v={BUILD_ID}">
<link rel="alternate" type="application/rss+xml" href="/index.xml" title="{esc(self.title)}">
<script>
  (function(){{var t=null;try{{t=localStorage.getItem('pref-theme')}}catch(e){{}}
  if(t==='dark'||(t!=='light'&&window.matchMedia('(prefers-color-scheme: dark)').matches))document.documentElement.classList.add('dark');}})();
</script>
{KATEX if math else ""}{extra_head}
</head>
<body class="{'list' if is_list else ''}" id="top">
{self.header(current)}
<main class="main">
{body}
</main>
{self.footer()}
<script src="/assets/main.js?v={BUILD_ID}"></script>
{LIVE_JS if LIVE_RELOAD else ""}
</body>
</html>
"""

    @staticmethod
    def meta(p: Post) -> str:
        date = f"{p.date:%B} {p.date.day}, {p.date.year}"
        return (f'<span title="{p.date.isoformat()}">{date}</span>&nbsp;·&nbsp;{p.minutes} 分鐘')

    def entry(self, p: Post, show_cover: bool = True) -> str:
        cover = ""
        if show_cover and p.cover.get("image"):
            cover = (f'<figure class="entry-cover"><img loading="lazy" src="{esc(p.cover["image"])}" '
                     f'alt="{esc(p.cover.get("alt", ""))}"></figure>')
        return f"""<article class="post-entry">
  {cover}
  <header class="entry-header"><h2 class="entry-hint-parent">{esc(p.title)}</h2></header>
  <div class="entry-content"><p>{esc(p.summary)}</p></div>
  <footer class="entry-footer">{self.meta(p)}</footer>
  <a class="entry-link" aria-label="post link to {esc(p.title)}" href="{esc(p.url)}"></a>
</article>"""

    def paginated(self, posts: list[Post], base_url: str, heading: str, *, show_cover=True,
                  crumbs: str = "", title: str = "") -> list[tuple[str, str]]:
        """回傳 [(網址, html)]，每頁 posts_per_page 篇。"""
        per = int(self.cfg.get("posts_per_page", 10))
        chunks = [posts[i:i + per] for i in range(0, len(posts), per)] or [[]]
        pages = []
        for n, chunk in enumerate(chunks, 1):
            url = base_url if n == 1 else f"{base_url}page/{n}/"
            nav = ""
            if len(chunks) > 1:
                prev = (f'<a class="prev" href="{base_url if n == 2 else f"{base_url}page/{n-1}/"}">«&nbsp;上一頁</a>'
                        if n > 1 else "")
                nxt = f'<a class="next" href="{base_url}page/{n+1}/">下一頁&nbsp;»</a>' if n < len(chunks) else ""
                nav = f'<footer class="page-footer"><nav class="pagination">{prev}{nxt}</nav></footer>'
            body = (f'<header class="page-header">{crumbs}<h1>{esc(heading)}</h1></header>'
                    + "".join(self.entry(p, show_cover) for p in chunk) + nav)
            pages.append((url, self.page(title=title or heading, body=body, current=base_url)))
        return pages

    # ---------- 各頁面 ----------

    def home(self) -> str:
        pr = self.cfg.get("profile", {})
        img = ""
        if pr.get("image"):
            img = (f'<img draggable="false" src="{esc(resolve_static(pr["image"]))}" alt="profile image" '
                   f'width="{pr.get("image_width", 150)}" height="{pr.get("image_height", 150)}">')
        socials = "".join(
            f'<a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer me" title="{esc(s["name"])}" '
            f'aria-label="{esc(s["name"])}">{SVG.get(s["name"].lower(), esc(s["name"]))}</a>'
            for s in self.cfg.get("social", [])
        )
        body = f"""<div class="profile"><div class="profile_inner">
  {img}
  <h1>{esc(pr.get("title", self.title))}</h1>
  <span>{esc(pr.get("subtitle", ""))}</span>
  <div class="social-icons">{socials}</div>
</div></div>"""
        return self.page(title=self.title, body=body, current="/")

    def single(self, i: int) -> str:
        p = self.posts[i]
        cover = ""
        if p.cover.get("image"):
            cap = f'<figcaption>{esc(p.cover["caption"])}</figcaption>' if p.cover.get("caption") else ""
            cover = (f'<figure class="entry-cover"><a href="{esc(p.cover["image"])}" target="_blank" rel="noopener noreferrer">'
                     f'<img loading="eager" src="{esc(p.cover["image"])}" alt="{esc(p.cover.get("alt", ""))}"></a>{cap}</figure>')
        tags = "".join(f'<li><a href="/tags/{esc(urlize(t))}/">{esc(t)}</a></li>' for t in p.tags)
        newer = self.posts[i - 1] if i > 0 else None
        older = self.posts[i + 1] if i + 1 < len(self.posts) else None
        nav = ""
        if newer or older:
            nav = '<nav class="paginav">'
            if newer:
                nav += (f'<a class="prev" href="{esc(newer.url)}"><span class="title">« 上一頁</span><br>'
                        f'<span>{esc(newer.title)}</span></a>')
            if older:
                nav += (f'<a class="next" href="{esc(older.url)}"><span class="title">下一頁 »</span><br>'
                        f'<span>{esc(older.title)}</span></a>')
            nav += "</nav>"
        share = "".join(
            f'<li><a href="#" data-share="{k}" aria-label="分享到 {label}" title="分享到 {label}">{SVG[k]}</a></li>'
            for k, label in (("x", "X"), ("linkedin", "LinkedIn"), ("facebook", "Facebook"))
        ) + f'<li><a href="#" data-share="copy" aria-label="複製連結" title="複製連結">{SVG["link"]}</a></li>'
        body = f"""<article class="post-single">
  <header class="post-header">
    <div class="breadcrumbs"><a href="/">首頁</a>&nbsp;»&nbsp;<a href="/posts/">Posts</a></div>
    <h1 class="post-title">{esc(p.title)}</h1>
    {f'<div class="post-description">{esc(p.description)}</div>' if p.description else ""}
    <div class="post-meta">{self.meta(p)}</div>
  </header>
  {cover}
  {toc_html(p.headings)}
  <div class="post-content">{p.html}</div>
  <footer class="post-footer">
    <ul class="post-tags">{tags}</ul>
    {nav}
    <ul class="share-buttons" data-title="{esc(p.title)}">{share}</ul>
  </footer>
</article>"""
        return self.page(title=p.title, body=body, current="/posts/", is_list=False,
                         description=p.summary, math=True)

    def archives(self) -> str:
        parts = ['<header class="page-header"><h1>Archive</h1></header>']
        by_year: dict[int, list[Post]] = {}
        for p in self.posts:
            by_year.setdefault(p.date.year, []).append(p)
        for year, ps in by_year.items():
            parts.append(f'<div class="archive-year"><h2 class="archive-year-header" id="{year}">'
                         f'<a class="archive-header-link" href="#{year}">{year}</a>'
                         f'<sup class="archive-count">&nbsp;{len(ps)}</sup></h2>')
            by_month: dict[str, list[Post]] = {}
            for p in ps:
                by_month.setdefault(f"{p.date:%B}", []).append(p)
            for month, mps in by_month.items():
                parts.append(f'<div class="archive-month"><h3 class="archive-month-header" id="{year}-{month}">'
                             f'<a class="archive-header-link" href="#{year}-{month}">{month}</a>'
                             f'<sup class="archive-count">&nbsp;{len(mps)}</sup></h3><div class="archive-posts">')
                for p in mps:
                    parts.append(f'<div class="archive-entry"><h3 class="archive-entry-title">{esc(p.title)}</h3>'
                                 f'<div class="archive-meta">{self.meta(p)}</div>'
                                 f'<a class="entry-link" aria-label="post link to {esc(p.title)}" href="{esc(p.url)}"></a></div>')
                parts.append("</div></div>")
            parts.append("</div>")
        return self.page(title="Archive", body="".join(parts), current="/archives/")

    def terms(self, kind: str, label: str, groups) -> str:
        items = "".join(
            f'<li><a href="/{kind}/{esc(slug)}/">{esc(name)} <sup><strong><sup>{len(ps)}</sup></strong></sup></a></li>'
            for slug, (name, ps) in groups.items()
        )
        body = f'<header class="page-header"><h1>{label}</h1></header><ul class="terms-tags">{items}</ul>'
        return self.page(title=label, body=body, current=f"/{kind}/")

    def search(self) -> str:
        body = """<header class="page-header"><h1>Search&nbsp;
<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
</h1></header>
<div id="searchbox">
  <input id="searchInput" autofocus placeholder="write something to search ..." aria-label="search" type="search" autocomplete="off" maxlength="64">
  <ul id="searchResults" aria-label="search results"></ul>
</div>"""
        return self.page(title="Search", body=body, current="/search/",
                         extra_head=f'<script defer src="/assets/search.js?v={BUILD_ID}"></script>')

    def not_found(self) -> str:
        body = '<div class="not-found">404</div>'
        return self.page(title="404 Page not found", body=body)

    def search_index(self) -> str:
        return json.dumps([
            {"title": p.title, "permalink": p.url, "summary": p.summary, "content": p.text,
             "tags": p.tags, "date": p.date.strftime("%Y-%m-%d")}
            for p in self.posts
        ], ensure_ascii=False)

    def rss(self) -> str:
        items = "".join(
            f"<item><title>{esc(p.title)}</title><link>{esc(self.base + quote(p.url))}</link>"
            f"<pubDate>{format_datetime(p.date)}</pubDate><guid>{esc(self.base + quote(p.url))}</guid>"
            f"<description>{esc(p.summary)}</description></item>"
            for p in self.posts[:20]
        )
        return (f'<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel>'
                f"<title>{esc(self.title)}</title><link>{esc(self.base + '/')}</link>"
                f"<language>{esc(self.cfg.get('language', 'zh-TW'))}</language>{items}</channel></rss>")

    def sitemap(self) -> str:
        urls = ["/", "/posts/", "/archives/", "/tags/", "/categories/", "/search/"] + [p.url for p in self.posts]
        body = "".join(f"<url><loc>{esc(self.base + quote(u))}</loc></url>" for u in urls)
        return f'<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>'


# ---------------------------------------------------------------------------
# 產生整個網站
# ---------------------------------------------------------------------------

def build(drafts: bool = False, future: bool = False) -> None:
    global BUILD_ID
    BUILD_ID = int(time.time() * 1000)
    t0 = time.time()
    cfg = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    posts = load_posts(cfg, drafts, future)
    site = Site(cfg, posts)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    # 靜態檔（圖片等）原樣複製
    if STATIC.exists():
        shutil.copytree(STATIC, OUT, dirs_exist_ok=True)
    out_assets = OUT / "assets"
    shutil.copytree(ASSETS, out_assets, dirs_exist_ok=True)
    pyg_css = HtmlFormatter(style="monokai").get_style_defs(".post-content .highlight")
    (out_assets / "style.css").write_text(
        (ASSETS / "style.css").read_text(encoding="utf-8") + "\n/* Pygments (monokai) */\n" + pyg_css,
        encoding="utf-8")

    def emit(url: str, content: str) -> None:
        write(OUT / unquote(url).strip("/") / "index.html", content)

    emit("/", site.home())
    for url, page in site.paginated(posts, "/posts/", "Posts",
                                    crumbs='<div class="breadcrumbs"><a href="/">首頁</a></div>'):
        emit(url, page)
    for i, p in enumerate(posts):
        emit(p.url, site.single(i))
    emit("/archives/", site.archives())
    emit("/tags/", site.terms("tags", "Tags", site.tags))
    emit("/categories/", site.terms("categories", "Categories", site.categories))
    crumb = lambda kind, label: (f'<div class="breadcrumbs"><a href="/">首頁</a>&nbsp;»&nbsp;'
                                 f'<a href="/{kind}/">{label}</a></div>')
    for slug, (name, ps) in site.tags.items():
        for url, page in site.paginated(ps, f"/tags/{slug}/", name, show_cover=False, crumbs=crumb("tags", "Tags")):
            emit(url, page)
    for slug, (name, ps) in site.categories.items():
        for url, page in site.paginated(ps, f"/categories/{slug}/", name, show_cover=False,
                                        crumbs=crumb("categories", "Categories")):
            emit(url, page)
    emit("/search/", site.search())
    write(OUT / "404.html", site.not_found())
    write(OUT / "index.json", site.search_index())
    write(OUT / "index.xml", site.rss())
    write(OUT / "sitemap.xml", site.sitemap())

    print(f"完成：{len(posts)} 篇文章、{len(site.tags)} 個標籤、{len(site.categories)} 個分類，"
          f"耗時 {time.time() - t0:.2f} 秒 → {OUT}")


# ---------------------------------------------------------------------------
# 本機伺服器 + 自動重建
# ---------------------------------------------------------------------------

def snapshot() -> dict[str, float]:
    files = {}
    for base in (CONTENT, STATIC, ASSETS):
        for f in base.rglob("*"):
            if f.is_file():
                files[str(f)] = f.stat().st_mtime
    for f in (CONFIG, Path(__file__)):
        files[str(f)] = f.stat().st_mtime
    return files


def lan_ip() -> str:
    """找出這台電腦在區網中的 IP（不會真的送出封包）。"""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def serve(port: int, drafts: bool, future: bool, lan: bool = False) -> None:
    global LIVE_RELOAD
    LIVE_RELOAD = True
    build(drafts, future)
    lock = threading.Lock()

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(OUT), **kw)

        def do_GET(self):
            if self.path == "/__build":
                data = str(BUILD_ID).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            with lock:
                target = Path(self.translate_path(self.path))
                if not target.exists():
                    data = (OUT / "404.html").read_bytes()
                    self.send_response(404)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                super().do_GET()

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def log_message(self, fmt, *args):
            pass

    def watch():
        last = snapshot()
        while True:
            time.sleep(1)
            now = snapshot()
            if now != last:
                last = now
                print("偵測到檔案變更，重新產生…")
                with lock:
                    try:
                        build(drafts, future)
                    except Exception as e:  # 寫錯 front matter 等情況不要讓伺服器掛掉
                        print(f"產生失敗：{e}")

    threading.Thread(target=watch, daemon=True).start()
    httpd = ThreadingHTTPServer(("0.0.0.0" if lan else "127.0.0.1", port), Handler)
    print(f"本機預覽：http://localhost:{port}/   （Ctrl+C 結束）")
    if lan:
        print(f"手機預覽（手機要連同一個 Wi-Fi）：http://{lan_ip()}:{port}/")
        print("  若手機打不開，請在 Windows 防火牆允許 Python 使用「私人網路」。")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


def new_post(title: str) -> None:
    now = datetime.now(TZ).replace(microsecond=0)
    name = f"{now:%Y%m%d}_{re.sub(r'[\\/:*?\"<>|]', '', title)}.md"
    path = CONTENT / name
    if path.exists():
        sys.exit(f"已經有這個檔案：{path}")
    path.write_text(
        f'+++\ntitle = "{title}"\ndate = {now.isoformat()}\ndraft = true\n'
        f'tags = []\ncategories = []\n\n[cover]\n    image = ""\n    alt = ""\n    caption = ""\n+++\n\n',
        encoding="utf-8")
    print(f"已建立 {path.relative_to(ROOT)}（draft = true，完成後記得改成 false）")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="自刻靜態網站產生器")
    ap.add_argument("command", nargs="?", default="build", choices=["build", "serve", "new"])
    ap.add_argument("title", nargs="?", help="new 指令用的文章標題")
    ap.add_argument("--port", type=int, default=1313)
    ap.add_argument("--drafts", action="store_true", help="包含草稿")
    ap.add_argument("--future", action="store_true", help="包含未來日期的文章")
    ap.add_argument("--lan", action="store_true", help="開放同一個 Wi-Fi 的手機、平板連線預覽")
    args = ap.parse_args()
    if args.command == "serve":
        serve(args.port, args.drafts, args.future, args.lan)
    elif args.command == "new":
        if not args.title:
            sys.exit('請給標題，例如：python build.py new "我的新文章"')
        new_post(args.title)
    else:
        build(args.drafts, args.future)


if __name__ == "__main__":
    main()
