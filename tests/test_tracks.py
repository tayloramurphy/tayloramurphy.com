import json
from pathlib import Path

TRACKS = Path(__file__).resolve().parents[1] / "source" / "tracks.json"


def test_tracks_file_has_real_circuits() -> None:
    data = json.loads(TRACKS.read_text(encoding="utf-8"))
    tracks = data["tracks"]
    ids = {t["id"] for t in tracks}
    names = " ".join(t["name"].lower() for t in tracks)

    assert len(tracks) >= 40
    assert "monaco" in names
    assert "spa" in names
    assert "daytona" in names
    assert "talladega" in names
    assert any("indianapolis" in t["id"] for t in tracks)

    for track in tracks:
        pts = track["points"]
        assert len(pts) >= 40, track["id"]
        assert all(0.0 <= x <= 1.0 and 0.0 <= y <= 1.0 for x, y in pts)
        assert track["id"]
        assert track["name"]
        assert track["series"]


def test_series_coverage_when_osm_present() -> None:
    data = json.loads(TRACKS.read_text(encoding="utf-8"))
    series = {tag for t in data["tracks"] for tag in t["series"]}
    assert "f1" in series
    names = " ".join(t["name"].lower() for t in data["tracks"])
    # Oval / endurance extras are added when OSM data is available.
    if "daytona" in names or "talladega" in names or "sarthe" in names:
        assert "nascar" in series or "wec" in series
