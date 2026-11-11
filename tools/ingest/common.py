"""Shared helpers for the local ingest tools: SQL output and state codes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "worker" / "src"))

# D1 rejects statements over 100,000 bytes; stay well inside it.
MAX_STATEMENT_BYTES = 90_000

# State FIPS -> postal code for the contiguous US and DC, the area the
# analysis grid covers. Alaska, Hawaii and the territories are deliberately
# absent.
CONUS_STATES = {
    "01": "AL", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT",
    "10": "DE", "11": "DC", "12": "FL", "13": "GA", "16": "ID", "17": "IL",
    "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME",
    "24": "MD", "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO",
    "30": "MT", "31": "NE", "32": "NV", "33": "NH", "34": "NJ", "35": "NM",
    "36": "NY", "37": "NC", "38": "ND", "39": "OH", "40": "OK", "41": "OR",
    "42": "PA", "44": "RI", "45": "SC", "46": "SD", "47": "TN", "48": "TX",
    "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV", "55": "WI",
    "56": "WY",
}  # fmt: skip


def sql_text(value):
    """Render a Python value as a SQL literal."""
    if value is None:
        return "NULL"
    if isinstance(value, (bytes, bytearray)):
        return f"X'{bytes(value).hex()}'"
    if isinstance(value, (int, float)):
        return repr(value)
    return "'" + str(value).replace("'", "''") + "'"


def write_inserts(f, table, columns, rows):
    """Write multi-row INSERTs to `f`, each under D1's statement size limit."""
    head = f"INSERT INTO {table} ({', '.join(columns)}) VALUES\n"
    batch, size = [], len(head)
    for row in rows:
        line = "(" + ",".join(sql_text(v) for v in row) + ")"
        if batch and size + len(line) + 2 > MAX_STATEMENT_BYTES:
            f.write(head + ",\n".join(batch) + ";\n")
            batch, size = [], len(head)
        batch.append(line)
        size += len(line) + 2
    if batch:
        f.write(head + ",\n".join(batch) + ";\n")


def write_tile_sql(path, dataset, layer, tiles):
    """Write a SQL file that replaces one dataset/layer of raster tiles.

    `tiles` yields (tx, ty, blob). The file first deletes the existing tiles
    for that dataset and layer, so reloading never leaves stale tiles behind.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(
            f"DELETE FROM raster_tiles WHERE dataset = {sql_text(dataset)} "
            f"AND layer = {sql_text(layer)};\n"
        )
        write_inserts(
            f,
            "raster_tiles",
            ("dataset", "layer", "ty", "tx", "data"),
            ((dataset, layer, ty, tx, blob) for tx, ty, blob in tiles),
        )
