from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

HIGHLIGHT_RE = re.compile(
    r"\{%\s*highlight\s+(\w+)\s*%\}\n?(.*?)\n?\{%\s*endhighlight\s*%\}",
    re.DOTALL,
)
MEDIA_HOST_RE = re.compile(
    r"https?://(?:www\.)?tayloramurphy\.com(?:/blog)?(/wp-content/[^\"')\s]+)",
    re.IGNORECASE,
)
FORMATTER = HtmlFormatter(nowrap=True, noclasses=False)


@dataclass(frozen=True)
class Post:
    source: Path
    title: str
    date: datetime
    permalink: str
    body: str
    published: bool

    @property
    def output_path(self) -> Path:
        slug = self.permalink.strip("/")
        return Path(slug) / "index.html"

    @property
    def year(self) -> int:
        return self.date.year

    @property
    def href(self) -> str:
        return self.permalink

    @property
    def venue(self) -> str | None:
        return None

    @property
    def external(self) -> bool:
        return False


@dataclass(frozen=True)
class Elsewhere:
    title: str
    date: datetime
    url: str
    venue: str

    @property
    def year(self) -> int:
        return self.date.year

    @property
    def href(self) -> str:
        return self.url

    @property
    def permalink(self) -> str:
        return self.url

    @property
    def external(self) -> bool:
        return True


def unescape_text(value: str) -> str:
    return html.unescape(value)


def convert_highlight_blocks(body: str) -> str:
    def repl(match: re.Match[str]) -> str:
        lang = match.group(1)
        code = match.group(2).rstrip("\n")
        return f"```{lang}\n{code}\n```"

    return HIGHLIGHT_RE.sub(repl, body)


def rewrite_media_urls(text: str) -> str:
    return MEDIA_HOST_RE.sub(r"\1", text)


def _highlight(code: str, lang: str, _attrs: str) -> str:
    try:
        lexer = get_lexer_by_name(lang)
    except ClassNotFound:
        lexer = get_lexer_by_name("text")
    return highlight(code, lexer, FORMATTER)


def render_markdown(body: str) -> str:
    md = MarkdownIt("commonmark", {"html": True, "highlight": _highlight})
    prepared = rewrite_media_urls(unescape_text(convert_highlight_blocks(body)))
    return md.render(prepared)


def _naive(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def _parse_date(raw: object, source: Path) -> datetime:
    if isinstance(raw, datetime):
        return _naive(raw)
    if isinstance(raw, str):
        return _naive(datetime.fromisoformat(raw))
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", source.name)
    if not match:
        raise ValueError(f"No date for {source}")
    year, month, day = (int(part) for part in match.groups())
    return datetime(year, month, day)


def _permalink(meta: dict, source: Path) -> str:
    raw = str(meta.get("permalink") or "").strip()
    if not raw:
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", source.stem)
        raw = slug
    if not raw.startswith("/"):
        raw = "/" + raw
    if not raw.endswith("/"):
        raw = raw + "/"
    return raw


def _prepare_frontmatter(fm: str) -> str:
    lines = []
    for line in fm.splitlines():
        match = re.match(r"^(title:\s*)(.+)$", line)
        if match and not match.group(2)[:1] in {"'", '"', "|", ">"}:
            value = match.group(2).replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{match.group(1)}"{value}"')
        else:
            lines.append(line)
    return "\n".join(lines)


def parse_post(path: Path) -> Post:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not text.startswith("---"):
        raise ValueError(f"Missing frontmatter: {path}")
    _, fm, body = text.split("---", 2)
    meta = yaml.safe_load(_prepare_frontmatter(fm)) or {}
    published = meta.get("published", True) is not False
    title = unescape_text(str(meta.get("title") or path.stem))
    return Post(
        source=path,
        title=title,
        date=_parse_date(meta.get("date"), path),
        permalink=_permalink(meta, path),
        body=body.lstrip("\n"),
        published=published,
    )


def load_elsewhere(path: Path) -> list[Elsewhere]:
    if not path.exists():
        return []
    rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    items: list[Elsewhere] = []
    for row in rows:
        raw = row["date"]
        if isinstance(raw, datetime):
            date = _naive(raw)
        else:
            date = _naive(datetime.fromisoformat(str(raw)))
        items.append(
            Elsewhere(
                title=str(row["title"]),
                date=date,
                url=str(row["url"]),
                venue=str(row.get("venue") or "Elsewhere"),
            )
        )
    return items


def load_posts(posts_dir: Path) -> list[Post]:
    posts = []
    for path in sorted(posts_dir.iterdir()):
        if path.suffix not in {".md", ".markdown"}:
            continue
        post = parse_post(path)
        if post.published:
            posts.append(post)
    posts.sort(key=lambda p: p.date, reverse=True)
    return posts
