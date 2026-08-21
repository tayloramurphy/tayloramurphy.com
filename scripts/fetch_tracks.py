"""Build source/tracks.json from real circuit geometry.

Sources:
- bacinger/f1-circuits GeoJSON (MIT)
- OpenStreetMap highway=raceway ways (ODbL)
"""

from __future__ import annotations

import json
import math
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "source" / "tracks.json"

SERIES = {
    "Circuit of the Americas": ["f1", "nascar", "wec", "indycar"],
    "Circuit de Spa-Francorchamps": ["f1", "wec"],
    "Bahrain International Circuit": ["f1", "wec"],
    "Autódromo José Carlos Pace - Interlagos": ["f1", "wec"],
    "Indianapolis Motor Speedway": ["f1", "indycar"],
    "Watkins Glen International": ["f1", "nascar", "indycar", "wec"],
    "Silverstone Circuit": ["f1", "wec"],
    "Shanghai International Circuit": ["f1", "wec"],
    "Losail International Circuit": ["f1", "wec"],
}


def slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def close_ring(pts: list[list[float]]) -> list[list[float]]:
    if len(pts) < 2:
        return pts
    if pts[0] != pts[-1]:
        return pts + [pts[0]]
    return pts


def rdp(points: list[list[float]], epsilon: float) -> list[list[float]]:
    if len(points) < 3:
        return points

    def dist(p, a, b) -> float:
        (x, y), (x1, y1), (x2, y2) = p, a, b
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(x - x1, y - y1)
        t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
        return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))

    def rec(pts: list[list[float]]) -> list[list[float]]:
        if len(pts) < 3:
            return pts
        a, b = pts[0], pts[-1]
        idx, dmax = 0, 0.0
        for i in range(1, len(pts) - 1):
            d = dist(pts[i], a, b)
            if d > dmax:
                idx, dmax = i, d
        if dmax > epsilon:
            left = rec(pts[: idx + 1])
            right = rec(pts[idx:])
            return left[:-1] + right
        return [a, b]

    return rec(points)


def normalize(lonlat: list[list[float]]) -> list[list[float]]:
    # lon/lat -> local meters-ish, flip y so north is up, then unit square with padding
    lons = [p[0] for p in lonlat]
    lats = [p[1] for p in lonlat]
    lat0 = sum(lats) / len(lats)
    k = math.cos(math.radians(lat0))
    xs = [(lon - min(lons)) * k for lon in lons]
    ys = [lat - min(lats) for lat in lats]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span = max(max_x - min_x, max_y - min_y) or 1.0
    pad = 0.08
    usable = 1.0 - 2 * pad
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2
    out = []
    for x, y in zip(xs, ys):
        nx = 0.5 + (x - cx) / span * usable
        ny = 0.5 - (y - cy) / span * usable  # flip: north up in source becomes smaller y on canvas? 
        # canvas y grows down. If north is up on a map, north should be smaller y.
        out.append([round(nx, 5), round(ny, 5)])
    return close_ring(out)


def from_linestring(coords: list) -> list[list[float]]:
    pts = [[float(c[0]), float(c[1])] for c in coords]
    simplified = rdp(pts, epsilon=0.00005)
    if len(simplified) < 90:
        step = max(1, len(pts) // 180)
        simplified = pts[::step]
    if len(simplified) > 360:
        simplified = rdp(simplified, epsilon=0.00012)
    return normalize(simplified)


def load_f1(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tracks = []
    for feat in data["features"]:
        props = feat.get("properties") or {}
        name = props.get("Name") or props.get("name")
        geom = feat.get("geometry") or {}
        if geom.get("type") != "LineString" or not name:
            continue
        points = from_linestring(geom["coordinates"])
        if len(points) < 40:
            continue
        tracks.append(
            {
                "id": slug(name),
                "name": name,
                "series": SERIES.get(name, ["f1"]),
                "points": points,
            }
        )
    return tracks


OSM_EXTRAS = {
    "daytona": ("Daytona International Speedway", ["nascar", "wec", "indycar"]),
    "talladega": ("Talladega Superspeedway", ["nascar"]),
    "bristol": ("Bristol Motor Speedway", ["nascar"]),
    "martinsville": ("Martinsville Speedway", ["nascar"]),
    "charlotte": ("Charlotte Motor Speedway", ["nascar"]),
    "sebring": ("Sebring International Raceway", ["wec", "indycar"]),
    "fuji": ("Fuji Speedway", ["wec"]),
    "barber": ("Barber Motorsports Park", ["indycar"]),
    "midohio": ("Mid-Ohio Sports Car Course", ["indycar"]),
    "sonoma": ("Sonoma Raceway", ["nascar", "indycar"]),
    "ims": ("Indianapolis Motor Speedway Oval", ["indycar", "nascar"]),
}

SKIP_NAME = re.compile(r"pit|kart|warmup|drift|chicane|short", re.I)


def _way_coords(way, nodes: dict) -> list[list[float]]:
    pts = []
    for nd in way.findall("nd"):
        node = nodes.get(nd.get("ref"))
        if node:
            pts.append([node[0], node[1]])
    return pts


def _score_way(tags: dict, n: int, closed: bool) -> int:
    name = tags.get("name") or ""
    if SKIP_NAME.search(name):
        return -1
    score = n
    if tags.get("highway") == "raceway":
        score += 200
        if name:
            score += 80
    if tags.get("leisure") == "stadium" and closed:
        score += 120
    if tags.get("leisure") == "sports_centre" and closed and n > 80:
        score += 40
    return score


def load_osm_xml(path: Path, display_name: str, series: list[str]) -> dict | None:
    import xml.etree.ElementTree as ET

    root = ET.parse(path).getroot()
    nodes = {
        n.get("id"): (float(n.get("lon")), float(n.get("lat")))
        for n in root.findall("node")
    }
    best = None
    best_score = 0
    for way in root.findall("way"):
        tags = {t.get("k"): t.get("v") for t in way.findall("tag")}
        refs = [nd.get("ref") for nd in way.findall("nd")]
        closed = bool(refs) and refs[0] == refs[-1]
        score = _score_way(tags, len(refs), closed)
        if score > best_score:
            coords = _way_coords(way, nodes)
            if len(coords) >= 30:
                best = coords
                best_score = score
    if not best:
        return None
    points = from_linestring(best)
    if len(points) < 40:
        return None
    return {
        "id": slug(display_name),
        "name": display_name,
        "series": series,
        "points": points,
    }


def load_osm_extracts(folder: Path) -> list[dict]:
    tracks = []
    for key, (name, series) in OSM_EXTRAS.items():
        path = folder / f"{key}.osm"
        if not path.exists():
            continue
        track = load_osm_xml(path, name, series)
        if track:
            tracks.append(track)
    return tracks


def main() -> None:
    f1 = Path("/tmp/tam-tracks/f1-circuits.geojson")
    tracks = load_f1(f1)
    seen = {t["id"] for t in tracks}
    for extra in load_osm_extracts(Path("/tmp/tam-tracks")):
        if extra["id"] not in seen:
            tracks.append(extra)
            seen.add(extra["id"])
    tracks.sort(key=lambda t: t["name"])
    OUT.write_text(json.dumps({"tracks": tracks}, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {len(tracks)} tracks -> {OUT}")
    for t in tracks:
        print(f"  {t['id']:40} {len(t['points']):4} pts  {','.join(t['series'])}")


if __name__ == "__main__":
    main()
