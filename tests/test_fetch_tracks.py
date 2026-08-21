"""Geometry helpers used to build source/tracks.json."""

from fetch_tracks import has_slash, nearly_closed, stitch_ways


def test_stitch_joins_and_reverses_ways_into_a_loop() -> None:
    a = (["1", "2", "3"], [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]])
    b = (["5", "4", "3"], [[2.0, 2.0], [2.0, 1.0], [2.0, 0.0]])
    c = (["5", "6", "1"], [[2.0, 2.0], [0.0, 2.0], [0.0, 0.0]])
    pts, leftover = stitch_ways([a, b, c])
    assert leftover == []
    assert pts[0] == pts[-1]
    assert len(pts) == 7


def test_circle_is_a_clean_loop() -> None:
    import math

    pts = [
        [0.5 + 0.3 * math.cos(a), 0.5 + 0.35 * math.sin(a)]
        for a in [i * math.tau / 48 for i in range(48)]
    ]
    pts.append(pts[0])
    assert nearly_closed(pts)
    assert not has_slash(pts)


def test_diagonal_close_is_a_slash() -> None:
    # Open creek-like path force-closed across the bounding box.
    pts = [[0.1, 0.1], [0.12, 0.3], [0.15, 0.55], [0.2, 0.9], [0.1, 0.1]]
    assert has_slash(pts)
