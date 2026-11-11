"""The reachable area as a coarse grid, for storing and for drawing on a map.

The search works on 250 m cells, which is more detail than a map needs and
too much to store per analysis. Each block of FACTOR x FACTOR cells keeps
the shortest road distance found inside it, as a level from 1 (at the start)
to LEVELS (at the full budget); 0 means nothing in the block was reached.

Blocks are aligned to the national grid, so block (bcol, brow) always covers
the same ground whichever analysis produced it.
"""

import struct
import zlib
from dataclasses import dataclass

from . import grid as g

FACTOR = 4  # cells per block side; must divide grid.TILE
BLOCK_M = g.CELL_M * FACTOR
BLOCKS_PER_TILE = g.TILE // FACTOR
LEVELS = 250
MAX_RUN = 32  # longest rectangle side, in blocks (see to_geojson)

_MAGIC = b"RBA1"
_HEADER = struct.Struct("<4siiHH")  # magic, bcol, brow, width, height


@dataclass
class Area:
    bcol: int  # block column of the west edge on the national grid
    brow: int  # block row of the south edge
    width: int
    height: int
    data: bytes  # one level per block, row-major starting from the south


def level(distance, budget):
    """The stored level for a search distance (both in search units)."""
    return 1 + distance * (LEVELS - 1) // budget


def crop(blocks, stride, c0, r0, c1, r1, bcol, brow):
    """Cut the inclusive block rectangle (c0, r0)-(c1, r1) out of a working
    grid `stride` blocks wide whose first block is (bcol, brow)."""
    data = b"".join(
        bytes(blocks[r * stride + c0 : r * stride + c1 + 1]) for r in range(r0, r1 + 1)
    )
    return Area(bcol + c0, brow + r0, c1 - c0 + 1, r1 - r0 + 1, data)


def encode(area):
    header = _HEADER.pack(_MAGIC, area.bcol, area.brow, area.width, area.height)
    return header + zlib.compress(area.data, 9)


def decode(blob):
    magic, bcol, brow, width, height = _HEADER.unpack_from(blob)
    if magic != _MAGIC:
        raise ValueError("not a stored reachable area")
    data = zlib.decompress(blob[_HEADER.size :])
    if len(data) != width * height:
        raise ValueError("stored reachable area is truncated")
    return Area(bcol, brow, width, height, data)


def _rectangles(area, bands):
    """Merge blocks of one band into rectangles: [(band, c0, c1, r0, r1)],
    with exclusive upper bounds, in block units relative to the area."""
    band_of = [-1] + [(v - 1) * bands // LEVELS for v in range(1, LEVELS + 1)]
    width, data = area.width, area.data
    rects = []
    below = {}  # (c0, c1, band) -> rectangle still growing upward
    for r in range(area.height):
        row = data[r * width : (r + 1) * width]
        current = {}
        c = 0
        while c < width:
            band = band_of[row[c]]
            if band < 0:
                c += 1
                continue
            c0 = c
            c += 1
            while c < width and c - c0 < MAX_RUN and band_of[row[c]] == band:
                c += 1
            key = (c0, c, band)
            rect = below.get(key)
            if rect is not None and r - rect[3] < MAX_RUN:
                rect[4] = r + 1
            else:
                rect = [band, c0, c, r, r + 1]
                rects.append(rect)
            current[key] = rect
        below = current
    return rects


def to_geojson(area, radius_m, bands=5):
    """The area as GeoJSON: one MultiPolygon feature per distance band.

    Band 0 is nearest the start. Polygons are grid-aligned rectangles, and a
    rectangle side never exceeds MAX_RUN blocks: the grid's straight edges
    are slightly curved on a web map, and short sides keep neighbouring
    rectangles from visibly gapping or overlapping.
    """
    corners = {}

    def corner(c, r):
        key = (c, r)
        if key not in corners:
            lon, lat = g.xy_to_lonlat(
                g.X0 + (area.bcol + c) * BLOCK_M, g.Y0 + (area.brow + r) * BLOCK_M
            )
            corners[key] = [round(lon, 5), round(lat, 5)]
        return corners[key]

    polygons = [[] for _ in range(bands)]
    for band, c0, c1, r0, r1 in _rectangles(area, bands):
        sw = corner(c0, r0)
        polygons[band].append(
            [[sw, corner(c1, r0), corner(c1, r1), corner(c0, r1), sw]]
        )
    features = [
        {
            "type": "Feature",
            "properties": {
                "band": band,
                "from_m": radius_m * band / bands,
                "to_m": radius_m * (band + 1) / bands,
            },
            "geometry": {"type": "MultiPolygon", "coordinates": coords},
        }
        for band, coords in enumerate(polygons)
        if coords
    ]
    return {"type": "FeatureCollection", "features": features}
