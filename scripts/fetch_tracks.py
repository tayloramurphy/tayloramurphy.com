"""Build source/tracks.json from real circuit geometry.

Sources:
- bacinger/f1-circuits GeoJSON (MIT)
- OpenStreetMap highway=raceway ways and type=circuit relations (ODbL)
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
    "Watkins Glen International": ["f1", "nascar", "indycar", "wec"],
    "Silverstone Circuit": ["f1", "wec"],
    "Shanghai International Circuit": ["f1", "wec"],
    "Losail International Circuit": ["f1", "wec"],
}

# bacinger's Indianapolis outline is the incomplete 2000 F1 layout (missing
# the east side of the oval). OSM circuit relations are complete.
SKIP_F1 = {"Indianapolis Motor Speedway"}

SKIP_NAME = re.compile(
    r"pit|kart|warmup|drift|chicane|short|dirt|creek|river|ig tc|"
    r"ドリフト|ショート|カート",
    re.I,
)


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


def nearly_closed(pts: list[list[float]], frac: float = 0.08) -> bool:
    if len(pts) < 3:
        return False
    if pts[0] == pts[-1]:
        return True
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    gap = math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1])
    return gap / diag < frac


def _point_to_seg(c: tuple[float, float], a: list[float], b: list[float]) -> float:
    cx, cy = c
    x1, y1 = a
    x2, y2 = b
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(cx - x1, cy - y1)
    t = max(0.0, min(1.0, ((cx - x1) * dx + (cy - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(cx - (x1 + t * dx), cy - (y1 + t * dy))


def has_slash(
    points: list[list[float]],
    min_len: float = 0.85,
    max_center_dist: float = 0.08,
) -> bool:
    """True when a long segment cuts through the middle of the bounding box.

    That pattern is the usual failure mode for a force-closed open OSM way
    (a creek, a half-oval, a pit lane) rather than a real circuit.
    """
    if len(points) < 4:
        return False
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    diag = math.hypot(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    center = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
    for a, b in zip(points, points[1:]):
        length = math.hypot(b[0] - a[0], b[1] - a[1])
        if length < min_len * diag:
            continue
        if _point_to_seg(center, a, b) < max_center_dist * diag:
            return True
    return False


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
    closed = lonlat[0] == lonlat[-1]
    for x, y in zip(xs, ys):
        nx = 0.5 + (x - cx) / span * usable
        ny = 0.5 - (y - cy) / span * usable
        out.append([round(nx, 5), round(ny, 5)])
    if closed or nearly_closed(out):
        return close_ring(out)
    return out


def from_linestring(coords: list) -> list[list[float]]:
    pts = [[float(c[0]), float(c[1])] for c in coords]
    closed = len(pts) >= 3 and pts[0] == pts[-1]
    work = pts[:-1] if closed else pts
    if len(work) < 3:
        return []
    simplified = rdp(work, epsilon=0.00005)
    if len(simplified) < 90:
        step = max(1, len(work) // 180)
        simplified = work[::step]
        if simplified[-1] != work[-1]:
            simplified.append(work[-1])
    if len(simplified) > 360:
        simplified = rdp(simplified, epsilon=0.00012)
    if closed or nearly_closed(simplified):
        simplified = close_ring(simplified)
    return normalize(simplified)


def stitch_ways(
    ways: list[tuple[list[str], list[list[float]]]],
) -> tuple[list[list[float]], list[tuple[list[str], list[list[float]]]]]:
    """Join ways by matching node ids, reversing as needed."""
    remaining = [(list(r), [list(p) for p in c]) for r, c in ways if len(r) >= 2 and len(c) >= 2]
    if not remaining:
        return [], []
    refs, coords = remaining.pop(0)
    path_refs = list(refs)
    path_coords = list(coords)
    used = True
    while remaining and used:
        used = False
        end, start = path_refs[-1], path_refs[0]
        for i, (r, c) in enumerate(remaining):
            if end == r[0]:
                path_refs.extend(r[1:])
                path_coords.extend(c[1:])
                remaining.pop(i)
                used = True
                break
            if end == r[-1]:
                path_refs.extend(reversed(r[:-1]))
                path_coords.extend(list(reversed(c[:-1])))
                remaining.pop(i)
                used = True
                break
            if start == r[-1]:
                path_refs = r[:-1] + path_refs
                path_coords = c[:-1] + path_coords
                remaining.pop(i)
                used = True
                break
            if start == r[0]:
                path_refs = list(reversed(r[1:])) + path_refs
                path_coords = list(reversed(c[1:])) + path_coords
                remaining.pop(i)
                used = True
                break
    return path_coords, remaining


def _good(points: list[list[float]]) -> bool:
    # Short ovals (Martinsville) only have ~30 racing-line nodes in OSM.
    return len(points) >= 24 and nearly_closed(points) and not has_slash(points)


def load_f1(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    tracks = []
    for feat in data["features"]:
        props = feat.get("properties") or {}
        name = props.get("Name") or props.get("name")
        geom = feat.get("geometry") or {}
        if geom.get("type") != "LineString" or not name:
            continue
        if name in SKIP_F1:
            continue
        points = from_linestring(geom["coordinates"])
        if not _good(points):
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


# (osm stem, display name, series, prefer "oval" | "road" | None)
OSM_TRACKS = [
    ("daytona", "Daytona International Speedway", ["nascar", "wec", "indycar"], "oval"),
    ("talladega", "Talladega Superspeedway", ["nascar"], "oval"),
    ("bristol", "Bristol Motor Speedway", ["nascar"], "oval"),
    ("martinsville", "Martinsville Speedway", ["nascar"], "oval"),
    ("charlotte", "Charlotte Motor Speedway", ["nascar"], "oval"),
    ("sebring", "Sebring International Raceway", ["wec", "indycar"], "road"),
    ("fuji", "Fuji Speedway", ["wec"], "road"),
    ("barber", "Barber Motorsports Park", ["indycar"], "road"),
    ("midohio", "Mid-Ohio Sports Car Course", ["indycar"], "road"),
    ("sonoma", "Sonoma Raceway", ["nascar", "indycar"], "road"),
    ("ims", "Indianapolis Motor Speedway Oval", ["indycar", "nascar"], "oval"),
    ("ims", "Indianapolis Motor Speedway Road Course", ["indycar", "f1"], "road"),
    ("nordschleife", "Nürburgring Nordschleife", ["wec"], "road"),
]


def _way_payload(way, nodes: dict) -> tuple[list[str], list[list[float]], dict] | None:
    tags = {t.get("k"): t.get("v") for t in way.findall("tag")}
    refs = [nd.get("ref") for nd in way.findall("nd")]
    coords = []
    for ref in refs:
        node = nodes.get(ref)
        if node:
            coords.append([node[0], node[1]])
    if len(coords) < 2:
        return None
    return refs, coords, tags


def _tokens(name: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", name.lower()))


def _relation_score(tags: dict, n_ways: int, display: str, prefer: str | None) -> int:
    name = tags.get("name") or ""
    if SKIP_NAME.search(name):
        return -1
    if tags.get("circuit") == "kart":
        return -1
    score = 10000 + n_ways * 20
    score += 40 * len(_tokens(display) & _tokens(name))
    kind = tags.get("circuit") or ""
    nlow = name.lower()
    if prefer == "oval":
        if kind == "oval" or "oval" in nlow:
            score += 400
        if kind == "road" or "road" in nlow or re.search(r"\brc\b", nlow):
            score -= 400
    elif prefer == "road":
        if kind == "road" or "road" in nlow or re.search(r"\brc\b", nlow):
            score += 400
        if kind == "oval" or ("oval" in nlow and "roval" not in nlow):
            score -= 400
    return score


def _closed_way_score(tags: dict, n: int, closed: bool, display: str, prefer: str | None) -> int:
    name = tags.get("name") or ""
    if SKIP_NAME.search(name):
        return -1
    hw = tags.get("highway")
    leisure = tags.get("leisure")
    sport = tags.get("sport") or ""
    if "kart" in sport.lower():
        return -1
    score = n
    if hw == "raceway":
        score += 5000
        if closed:
            score += 400
        if name:
            score += 80
    elif leisure in {"stadium", "sports_centre"} and closed and "motor" in sport:
        score += 2000
    else:
        return -1
    score += 40 * len(_tokens(display) & _tokens(name))
    nlow = name.lower()
    if prefer == "oval" and re.search(r"roval|road|\brc\b", nlow):
        score -= 500
    if prefer == "road" and "oval" in nlow and "roval" not in nlow:
        score -= 500
    return score


def extract_osm(path: Path, display_name: str, prefer: str | None) -> list[list[float]] | None:
    import xml.etree.ElementTree as ET

    root = ET.parse(path).getroot()
    nodes = {
        n.get("id"): (float(n.get("lon")), float(n.get("lat")))
        for n in root.findall("node")
    }
    ways = {}
    for way in root.findall("way"):
        payload = _way_payload(way, nodes)
        if payload:
            ways[way.get("id")] = payload

    candidates: list[tuple[int, list[list[float]]]] = []
    stadiums: list[tuple[int, list[list[float]]]] = []

    for rel in root.findall("relation"):
        tags = {t.get("k"): t.get("v") for t in rel.findall("tag")}
        rel_name = tags.get("name") or ""
        is_circuit = tags.get("type") == "circuit" or tags.get("route") == "raceway"
        named_route = tags.get("type") == "route" and len(_tokens(display_name) & _tokens(rel_name)) >= 2
        if not is_circuit and not named_route:
            continue
        members = []
        for member in rel.findall("member"):
            if member.get("type") != "way":
                continue
            payload = ways.get(member.get("ref"))
            if not payload:
                continue
            refs, coords, wtags = payload
            if SKIP_NAME.search(wtags.get("name") or ""):
                continue
            members.append((refs, coords))
        if not members:
            continue
        score = _relation_score(tags, len(members), display_name, prefer)
        if score < 0:
            continue
        coords, _leftover = stitch_ways(members)
        if not coords:
            continue
        points = from_linestring(coords)
        if _good(points):
            candidates.append((score, points))

    for _wid, (refs, coords, tags) in ways.items():
        closed = bool(refs) and refs[0] == refs[-1]
        score = _closed_way_score(tags, len(refs), closed, display_name, prefer)
        if score < 0:
            continue
        points = from_linestring(coords)
        if not _good(points):
            continue
        if tags.get("leisure") in {"stadium", "sports_centre"}:
            stadiums.append((score, points))
        else:
            candidates.append((score, points))

    raceways = [
        (refs, coords)
        for _wid, (refs, coords, tags) in ways.items()
        if tags.get("highway") == "raceway" and not SKIP_NAME.search(tags.get("name") or "")
    ]
    if raceways:
        raceways.sort(key=lambda item: -len(item[0]))
        coords, leftover = stitch_ways(raceways)
        if coords:
            points = from_linestring(coords)
            if _good(points):
                # leftover fragments (pit stubs, cut-throughs) are ok if
                # the main chain already formed a loop
                candidates.append((3000 - len(leftover), points))

    if not candidates:
        candidates.extend(stadiums)

    if not candidates:
        return None
    candidates.sort(key=lambda item: -item[0])
    return candidates[0][1]


def load_osm_extracts(folder: Path) -> list[dict]:
    tracks = []
    for stem, name, series, prefer in OSM_TRACKS:
        path = folder / f"{stem}.osm"
        if not path.exists():
            continue
        points = extract_osm(path, name, prefer)
        if not points:
            continue
        tracks.append(
            {
                "id": slug(name),
                "name": name,
                "series": series,
                "points": points,
            }
        )
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
        print(f"  {t['id']:48} {len(t['points']):4} pts  {','.join(t['series'])}")


if __name__ == "__main__":
    main()
