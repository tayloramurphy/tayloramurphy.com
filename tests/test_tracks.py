import json
from pathlib import Path

from fetch_tracks import has_slash, nearly_closed

TRACKS = Path(__file__).resolve().parents[1] / "source" / "tracks.json"


def _load():
    return json.loads(TRACKS.read_text(encoding="utf-8"))["tracks"]


def test_tracks_file_has_real_circuits() -> None:
    tracks = _load()
    names = " ".join(t["name"].lower() for t in tracks)

    assert len(tracks) >= 40
    assert "monaco" in names
    assert "spa" in names
    assert "daytona" in names
    assert "talladega" in names
    assert "nordschleife" in names
    assert any("indianapolis" in t["id"] for t in tracks)

    for track in tracks:
        pts = track["points"]
        assert len(pts) >= 24, track["id"]
        assert all(0.0 <= x <= 1.0 and 0.0 <= y <= 1.0 for x, y in pts)
        assert track["id"]
        assert track["name"]
        assert track["series"]
        assert nearly_closed(pts), track["id"]
        assert not has_slash(pts), track["id"]


def test_indianapolis_oval_is_a_rounded_rectangle() -> None:
    oval = next(t for t in _load() if "indianapolis" in t["id"] and "oval" in t["id"])
    xs = [p[0] for p in oval["points"]]
    ys = [p[1] for p in oval["points"]]
    aspect = (max(xs) - min(xs)) / (max(ys) - min(ys))
    # IMS is a rounded rectangle, longer north-south than east-west.
    assert 0.28 <= aspect <= 0.55, aspect
    assert oval["points"][0] == oval["points"][-1]


def test_nordschleife_is_the_long_north_loop() -> None:
    tracks = _load()
    nord = next(t for t in tracks if "nordschleife" in t["id"])
    gp = next(t for t in tracks if t["id"] == "nurburgring")
    assert nord["name"] == "Nürburgring Nordschleife"
    # GP-Strecke is ~5 km; the North Loop is ~21 km and must keep more of the outline.
    assert len(nord["points"]) >= 150
    assert len(nord["points"]) > len(gp["points"])
    assert nord["points"][0] == nord["points"][-1]


def test_martinsville_is_a_paperclip_not_the_grandstands() -> None:
    mart = next(t for t in _load() if "martinsville" in t["id"])
    xs = [p[0] for p in mart["points"]]
    ys = [p[1] for p in mart["points"]]
    aspect = (max(xs) - min(xs)) / (max(ys) - min(ys))
    # Racing line is a short paperclip. The stadium footprint is notched
    # and kept more vertices for the grandstand inlets.
    assert 24 <= len(mart["points"]) <= 36
    assert 0.45 <= aspect <= 0.75
    assert mart["points"][0] == mart["points"][-1]


def test_home_header_is_name_and_roles() -> None:
    home = (Path(__file__).resolve().parents[1] / "source" / "templates" / "home.html").read_text(
        encoding="utf-8"
    )
    base = (Path(__file__).resolve().parents[1] / "source" / "templates" / "base.html").read_text(
        encoding="utf-8"
    )
    assert "<h1>Taylor A Murphy</h1>" in home
    assert "Engineer, Founder, Dad" in home
    assert "Taylor A Murphy." not in home
    assert "goofy ambitious dad" not in home
    assert "Taylor A Murphy" in base
    assert 'rel="icon" href="/favicon.svg"' in base
    assert "Taylor A. Murphy" not in base


def test_home_selected_writing_is_recent_work() -> None:
    home = (Path(__file__).resolve().parents[1] / "source" / "templates" / "home.html").read_text(
        encoding="utf-8"
    )
    assert "What happens when a PM runs a coding agent" in home
    assert "Being present isn't enough to slow time" in home
    assert "Goodbye Arch. Long live Meltano." in home
    assert "Analytics should be an Assembly Line" in home
    assert "Lessons learned managing the GitLab Data team" in home
    assert "thoughts-on-identity" not in home
    assert "meltano-introduction" not in home


def test_track_script_freezes_lights_on_reading_pages() -> None:
    js = (Path(__file__).resolve().parents[1] / "source" / "track.js").read_text(
        encoding="utf-8"
    )
    assert "dataset.trackMotion" in js
    assert '=== "still"' in js


def test_track_label_css_wraps_instead_of_truncating() -> None:
    css = (Path(__file__).resolve().parents[1] / "source" / "homepage.css").read_text(
        encoding="utf-8"
    )
    block = css.split(".track-label")[1].split("}")[0]
    assert "nowrap" not in block
    assert "ellipsis" not in block
    assert "text-wrap" in block or "white-space: normal" in block


def test_series_coverage_when_osm_present() -> None:
    data = json.loads(TRACKS.read_text(encoding="utf-8"))
    series = {tag for t in data["tracks"] for tag in t["series"]}
    assert "f1" in series
    names = " ".join(t["name"].lower() for t in data["tracks"])
    # Oval / endurance extras are added when OSM data is available.
    if "daytona" in names or "talladega" in names or "sarthe" in names:
        assert "nascar" in series or "wec" in series
