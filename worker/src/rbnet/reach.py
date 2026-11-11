"""Road-distance reachability over a rasterized road grid.

Deterministic replacement for the legacy random-walk pather: a shortest-path
search across road cells, moving between the eight touching neighbours, that
stops at a distance budget. Pure standard library so it runs unchanged in the
Python Worker and under ordinary CPython tests.
"""

import sys
from array import array

# Step costs in integer units of one fifth of a cell (50 m at 250 m cells):
# 5 for an orthogonal step, 7 for a diagonal (7/5 = 1.40 vs sqrt(2) = 1.414).
UNITS_PER_CELL = 5
ORTHO = 5
DIAG = 7
UNREACHED = 0xFFFF


def build_mosaic(tiles, tx0, ty0, ntx, nty, tile, typecode="B"):
    """Stitch tiles into one row-major grid with a one-cell empty border.

    `tiles` maps (tx, ty) -> the tile's raw cell bytes (row 0 = south), one
    byte per cell for typecode "B" or little-endian uint16 for "H". Missing
    tiles are left as zeros. Returns (grid, width, height). The border means
    the search never has to bounds-check a neighbour.
    """
    width = ntx * tile + 2
    height = nty * tile + 2
    if typecode == "B":
        grid = bytearray(width * height)
    else:
        grid = array(typecode, bytes(width * height * array(typecode).itemsize))
    for (tx, ty), data in tiles.items():
        if typecode != "B":
            cells = array(typecode)
            cells.frombytes(data)
            if sys.byteorder == "big":
                cells.byteswap()
            data = cells
        col0 = 1 + (tx - tx0) * tile
        row0 = 1 + (ty - ty0) * tile
        for r in range(tile):
            dst = (row0 + r) * width + col0
            grid[dst : dst + tile] = data[r * tile : (r + 1) * tile]
    return grid, width, height


def snap_to_road(grid, width, height, index, max_cells):
    """Nearest road cell to `index` within `max_cells` rings, or -1."""
    if grid[index]:
        return index
    row, col = divmod(index, width)
    for ring in range(1, max_cells + 1):
        best, best_d2 = -1, None
        for dr in range(-ring, ring + 1):
            r = row + dr
            if r < 1 or r >= height - 1:
                continue
            edge = abs(dr) == ring
            for dc in range(-ring, ring + 1) if edge else (-ring, ring):
                c = col + dc
                if c < 1 or c >= width - 1:
                    continue
                if grid[r * width + c]:
                    d2 = dr * dr + dc * dc
                    if best_d2 is None or d2 < best_d2:
                        best, best_d2 = r * width + c, d2
        if best >= 0:
            return best
    return -1


def reach(grid, width, start, budget):
    """Shortest road distance from `start` to every road cell within `budget`.

    `grid` is row-major with a one-cell empty border (see `build_mosaic`);
    any non-zero cell is a road. `budget` is in step-cost units. Returns an
    array of distances, UNREACHED where the cell is not reachable in budget.
    """
    if budget >= UNREACHED:
        raise ValueError("budget too large for 16-bit distances")
    dist = array("H", [UNREACHED]) * len(grid)
    # One bucket per distance value: with small integer step costs this is
    # cheaper than a heap and visits cells in exact distance order.
    buckets = [None] * (budget + 1)
    dist[start] = 0
    buckets[0] = [start]
    steps = (
        (1, ORTHO),
        (-1, ORTHO),
        (width, ORTHO),
        (-width, ORTHO),
        (width + 1, DIAG),
        (width - 1, DIAG),
        (-width + 1, DIAG),
        (-width - 1, DIAG),
    )
    for d in range(budget + 1):
        bucket = buckets[d]
        if bucket is None:
            continue
        buckets[d] = None
        for i in bucket:
            if dist[i] != d:
                continue  # stale entry; a shorter route was found later
            for off, cost in steps:
                j = i + off
                nd = d + cost
                if nd < dist[j] and nd <= budget and grid[j]:
                    dist[j] = nd
                    target = buckets[nd]
                    if target is None:
                        buckets[nd] = [j]
                    else:
                        target.append(j)
    return dist
