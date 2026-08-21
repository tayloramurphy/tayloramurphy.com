from __future__ import annotations

import argparse
import shutil
from collections import defaultdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pygments.formatters import HtmlFormatter

from tamweb.posts import load_elsewhere, load_posts, render_markdown

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def _env(templates: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(templates),
        autoescape=select_autoescape(["html"]),
    )


def _copy_static(root: Path, source: Path, public: Path) -> None:
    if public.exists():
        shutil.rmtree(public)
    public.mkdir(parents=True)
    shutil.copy2(source / "homepage.css", public / "styles.css")
    shutil.copy2(source / "track.js", public / "track.js")
    headers = source / "_headers"
    if headers.exists():
        shutil.copy2(headers, public / "_headers")
    tracks = source / "tracks.json"
    if tracks.exists():
        shutil.copy2(tracks, public / "tracks.json")
    shutil.copytree(source / "fonts", public / "fonts")
    shutil.copytree(source / "img", public / "img")
    shutil.copytree(root / "wp-content", public / "wp-content")
    syntax = HtmlFormatter(style="native").get_style_defs(".highlight")
    (public / "syntax.css").write_text(
        syntax
        + "\n.highlight { background: transparent; }\n"
        + ".highlight pre { margin: 0; }\n",
        encoding="utf-8",
    )


def build(root: Path | None = None) -> Path:
    root = (root or PACKAGE_ROOT).resolve()
    source = root / "source"
    public = root / "public"
    _copy_static(root, source, public)
    env = _env(source / "templates")
    posts = load_posts(root / "_posts")
    elsewhere = load_elsewhere(source / "elsewhere.yaml")
    rendered = [(post, render_markdown(post.body)) for post in posts]

    home = env.get_template("home.html").render(
        page_title="Taylor A. Murphy",
    )
    (public / "index.html").write_text(home, encoding="utf-8")

    index_entries = [*posts, *elsewhere]
    index_entries.sort(key=lambda item: item.date, reverse=True)
    by_year: dict[int, list] = defaultdict(list)
    for item in index_entries:
        by_year[item.year].append(item)
    writing = env.get_template("writing.html").render(
        page_title="Writing — Taylor A. Murphy",
        years=sorted(by_year.keys(), reverse=True),
        by_year=by_year,
        count=len(index_entries),
    )
    writing_dir = public / "writing"
    writing_dir.mkdir(parents=True)
    (writing_dir / "index.html").write_text(writing, encoding="utf-8")

    post_tmpl = env.get_template("post.html")
    for post, html in rendered:
        out = public / post.output_path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            post_tmpl.render(
                page_title=f"{post.title} — Taylor A. Murphy",
                post=post,
                body=html,
            ),
            encoding="utf-8",
        )

    not_found = env.get_template("404.html").render(
        page_title="Not found — Taylor A. Murphy",
    )
    (public / "404.html").write_text(not_found, encoding="utf-8")
    return public


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args()
    dest = build(args.root)
    print(f"built {dest}")


if __name__ == "__main__":
    main()
