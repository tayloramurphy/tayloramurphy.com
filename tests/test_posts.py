import re
import shutil
from datetime import datetime
from pathlib import Path

import pytest

from tamweb.posts import (
    convert_highlight_blocks,
    load_elsewhere,
    load_posts,
    parse_post,
    render_markdown,
    rewrite_media_urls,
    unescape_text,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_permalink_date_and_title(tmp_path: Path) -> None:
    path = tmp_path / "2018-08-01-meltano.md"
    path.write_text(
        "---\n"
        "title: Introducing Meltano\n"
        "date: 2018-08-01T13:21:00+00:00\n"
        "permalink: /meltano-introduction/\n"
        "---\n"
        "Hello **world**.\n",
        encoding="utf-8",
    )
    post = parse_post(path)
    assert post.permalink == "/meltano-introduction/"
    assert post.output_path == Path("meltano-introduction/index.html")
    assert post.title == "Introducing Meltano"
    assert post.date == datetime(2018, 8, 1, 13, 21)
    assert post.published is True
    assert "Hello **world**." in post.body


def test_unpublished_posts_are_skipped(tmp_path: Path) -> None:
    published = tmp_path / "2018-08-01-a.md"
    published.write_text(
        "---\ntitle: A\ndate: 2018-08-01\npermalink: /a/\n---\nHi\n",
        encoding="utf-8",
    )
    stub = tmp_path / "2015-11-18-stub.md"
    stub.write_text(
        "---\npublished: false\ntitle: Stub\n---\nStuff\n",
        encoding="utf-8",
    )
    posts = load_posts(tmp_path)
    assert [p.permalink for p in posts] == ["/a/"]


def test_html_entities_in_titles_are_unescaped() -> None:
    assert unescape_text("Let&#8217;s Be Realistic") == "Let’s Be Realistic"


def test_highlight_tags_become_fenced_blocks() -> None:
    raw = "{% highlight python %}\nprint(1)\n{% endhighlight %}\n"
    assert convert_highlight_blocks(raw) == "```python\nprint(1)\n```\n"


def test_wordpress_media_urls_become_local() -> None:
    html = (
        '<img src="http://tayloramurphy.com/blog/wp-content/uploads/2017/08/IMG.jpg" '
        'srcset="http://www.tayloramurphy.com/blog/wp-content/uploads/2017/08/IMG-300.jpg 300w">'
    )
    out = rewrite_media_urls(html)
    assert "http://tayloramurphy.com" not in out
    assert 'src="/wp-content/uploads/2017/08/IMG.jpg"' in out
    assert "/wp-content/uploads/2017/08/IMG-300.jpg" in out


def test_markdown_keeps_html_and_highlights_code() -> None:
    html = render_markdown(
        "<p>Already HTML.</p>\n\n"
        "{% highlight python %}\nprint(1)\n{% endhighlight %}\n"
    )
    assert "<p>Already HTML.</p>" in html
    assert "print" in html
    assert "<pre" in html


def test_elsewhere_yaml_is_links_not_copies() -> None:
    items = load_elsewhere(Path(__file__).resolve().parents[1] / "source" / "elsewhere.yaml")
    assert len(items) >= 7
    urls = [item.url for item in items]
    assert any("substack.com" in url for url in urls)
    assert any("dadambition.substack.com" in url for url in urls)
    assert all(url.startswith("https://") for url in urls)
    assert all(item.external for item in items)
    assert all(item.venue for item in items)


def test_build_writes_permalink_directories(tmp_path: Path) -> None:
    posts = tmp_path / "_posts"
    posts.mkdir()
    (posts / "2018-08-01-meltano.md").write_text(
        "---\ntitle: Introducing Meltano\ndate: 2018-08-01\npermalink: /meltano-introduction/\n---\nHello.\n",
        encoding="utf-8",
    )
    source = tmp_path / "source"
    shutil.copytree(Path(__file__).resolve().parents[1] / "source", source)
    (tmp_path / "wp-content").mkdir()
    from tamweb.build import build

    dest = build(tmp_path)
    assert (dest / "index.html").is_file()
    assert (dest / "writing" / "index.html").is_file()
    assert (dest / "meltano-introduction" / "index.html").is_file()
    assert (dest / "favicon.svg").is_file()
    assert (dest / "favicon.ico").is_file()
    assert (dest / "apple-touch-icon.png").is_file()
    home = (dest / "index.html").read_text(encoding="utf-8")
    assert "<title>Taylor A Murphy</title>" in home
    assert "Taylor A. Murphy" not in home
    assert 'href="/favicon.svg"' in home
    assert 'data-track-motion="still"' not in home
    html = (dest / "meltano-introduction" / "index.html").read_text(encoding="utf-8")
    assert "Introducing Meltano" in html
    assert "<title>Introducing Meltano — Taylor A Murphy</title>" in html
    assert "Hello." in html
    assert 'data-track-motion="still"' in html
    writing = (dest / "writing" / "index.html").read_text(encoding="utf-8")
    assert "<title>Writing — Taylor A Murphy</title>" in writing
    assert "substack.com" in writing
    assert "Substack" in writing
    assert 'data-track-motion="still"' not in writing
    assert "#FF3B30" in (dest / "styles.css").read_text(encoding="utf-8")
    assert "#3DFFB0" not in (dest / "styles.css").read_text(encoding="utf-8")


def test_real_archive_has_unique_permalinks() -> None:
    root = Path(__file__).resolve().parents[1] / "_posts"
    posts = load_posts(root)
    permalinks = [p.permalink for p in posts]
    assert len(posts) >= 100
    assert len(permalinks) == len(set(permalinks))
    assert all(p.permalink.startswith("/") and p.permalink.endswith("/") for p in posts)
    assert all(p.published for p in posts)
    assert "/meltano-introduction/" in permalinks
    assert "/the-beginning/" in permalinks
    assert "/okrs/" in permalinks


def test_gitlab_blog_links_use_dateless_paths() -> None:
    root = Path(__file__).resolve().parents[1] / "_posts"
    dated = []
    for path in sorted(root.iterdir()):
        if path.suffix not in {".md", ".markdown"}:
            continue
        dated.extend(
            re.findall(
                r"https://about\.gitlab\.com/blog/\d{4}/\d{2}/\d{2}/[^\s)\"']+",
                path.read_text(encoding="utf-8"),
            )
        )
    assert dated == []
    meltano = (root / "2018-08-01-meltano-tool.md").read_text(encoding="utf-8")
    assert (
        "https://about.gitlab.com/blog/hey-data-teams-we-are-working-on-a-tool-just-for-you/"
        in meltano
    )
