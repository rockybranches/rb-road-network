#!/usr/bin/env python3
"""Download the roads layer of every Geofabrik extract for the contiguous US.

Standard library only. Each state's `-latest-free.shp.zip` holds eighteen
layers, of which the analysis needs one, so this reads the archive's file
list with a ranged request and downloads only `gis_osm_roads_free_1.*`:
about a fifth of the archive.

    fetch_roads.py --out "$RB_DATA/gis_osm_roads_2026-11"
    fetch_roads.py --out DIR --regions delaware rhode-island

Each extract lands in `DIR/<region>/`, and `DIR/sources.json` records the
dated archive each one came from. Files that are already complete are left
alone, so an interrupted run can simply be started again. Requests are made
one at a time; Geofabrik asks bulk users not to download in parallel.
"""

import argparse
import io
import json
import struct
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import zlib
from pathlib import Path

from common import CONUS_STATES

INDEX_URL = "https://download.geofabrik.de/index-v1-nogeom.json"
LAYER = "gis_osm_roads_free_1"
USER_AGENT = "rb-road-network-ingest"
TIMEOUT_S = 120
# The file list sits at the end of the archive; this is far more than it needs.
TAIL_BYTES = 1 << 20
LOCAL_HEADER = struct.Struct("<4s5H3I2H")
ATTEMPTS = 4


def conus_extracts(index):
    """Return {region: shapefile archive URL} covering the contiguous US.

    `index` is Geofabrik's index-v1 document. A state without an archive of
    its own (California) is covered by its sub-regions instead.
    """
    wanted = {f"US-{code}" for code in CONUS_STATES.values()}
    props = [f["properties"] for f in index["features"]]
    extracts = {}
    for p in props:
        if not wanted.intersection(p.get("iso3166-2") or ()):
            continue
        url = p.get("urls", {}).get("shp")
        if url:
            extracts[p["id"].split("/")[-1]] = url
            continue
        parts = {
            c["id"].split("/")[-1]: c["urls"]["shp"]
            for c in props
            if c.get("parent") == p["id"] and c.get("urls", {}).get("shp")
        }
        if not parts:
            raise SystemExit(f"no shapefile archive for {p['id']} or its sub-regions")
        extracts.update(parts)
    return extracts


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def _request(url, headers=None, method="GET"):
    return urllib.request.Request(
        url, headers={"user-agent": USER_AGENT, **(headers or {})}, method=method
    )


def resolve_dated(url):
    """Follow the `-latest-` redirect once, so every request for one archive
    reads the same dated file even if a new one is published meanwhile."""
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(_request(url, method="HEAD"), timeout=TIMEOUT_S):
            return url
    except urllib.error.HTTPError as exc:
        target = exc.headers.get("location")
        if 300 <= exc.code < 400 and target:
            return urllib.parse.urljoin(url, target)
        raise


def http_range(url):
    """Return open_range(start, end) for `url`; `end` is inclusive, and a
    negative `start` with no `end` asks for that many bytes from the end."""

    def open_range(start, end=None):
        spec = f"bytes={start}" if end is None else f"bytes={start}-{end}"
        resp = urllib.request.urlopen(_request(url, {"range": spec}), timeout=TIMEOUT_S)
        if resp.status != 206:
            resp.close()
            raise OSError(f"{url}: server ignored the range request")
        return resp

    return open_range


class _Tail(io.RawIOBase):
    """The last bytes of a remote file, addressed by their real offsets."""

    def __init__(self, data, total):
        self._data, self._total, self._pos = data, total, total
        self._base = total - len(data)

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self._pos

    def seek(self, offset, whence=io.SEEK_SET):
        base = {io.SEEK_SET: 0, io.SEEK_CUR: self._pos, io.SEEK_END: self._total}[whence]
        self._pos = base + offset
        return self._pos

    def read(self, n=-1):
        if self._pos < self._base:
            raise OSError("archive file list is larger than the part downloaded")
        start = self._pos - self._base
        chunk = self._data[start:] if n is None or n < 0 else self._data[start : start + n]
        self._pos += len(chunk)
        return chunk


def list_members(open_range):
    """Return (entries sorted by position, offset where the file list starts)."""
    with open_range(-TAIL_BYTES) as resp:
        data = resp.read()
        total = int(resp.headers["content-range"].rsplit("/", 1)[1])
    with zipfile.ZipFile(_Tail(data, total)) as zf:
        return sorted(zf.infolist(), key=lambda i: i.header_offset), zf.start_dir


def fetch_member(open_range, info, end, dest):
    """Download one archive member to `dest`, checking its size and checksum.

    `end` is the offset just past this member's data: the next member's
    header, or the start of the file list.
    """
    if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
        raise OSError(f"{info.filename}: unsupported compression {info.compress_type}")
    part = dest.with_name(dest.name + ".part")
    with open_range(info.header_offset, end - 1) as resp, part.open("wb") as out:
        fields = LOCAL_HEADER.unpack(resp.read(LOCAL_HEADER.size))
        if fields[0] != b"PK\x03\x04":
            raise OSError(f"{info.filename}: not at a file header")
        resp.read(fields[9] + fields[10])  # name and extra field
        inflate = zlib.decompressobj(-15) if info.compress_type == zipfile.ZIP_DEFLATED else None
        left, crc, size = info.compress_size, 0, 0
        while left:
            chunk = resp.read(min(left, 1 << 20))
            if not chunk:
                raise OSError(f"{info.filename}: download ended early")
            left -= len(chunk)
            if inflate:
                chunk = inflate.decompress(chunk)
            crc = zlib.crc32(chunk, crc)
            size += len(chunk)
            out.write(chunk)
        if inflate:
            chunk = inflate.flush()
            crc = zlib.crc32(chunk, crc)
            size += len(chunk)
            out.write(chunk)
    if size != info.file_size or crc != info.CRC:
        part.unlink()
        raise OSError(f"{info.filename}: size or checksum does not match the archive")
    part.replace(dest)


def fetch_layer(open_range, dest_dir, layer=LAYER):
    """Download every file of `layer` into `dest_dir`. Returns bytes fetched."""
    entries, dir_start = list_members(open_range)
    ends = [e.header_offset for e in entries[1:]] + [dir_start]
    wanted = [(e, end) for e, end in zip(entries, ends) if Path(e.filename).stem == layer]
    if not any(e.filename.endswith(".shp") for e, _ in wanted):
        raise OSError(f"archive has no {layer}.shp")
    dest_dir.mkdir(parents=True, exist_ok=True)
    fetched = 0
    for info, end in wanted:
        dest = dest_dir / Path(info.filename).name
        if dest.exists() and dest.stat().st_size == info.file_size:
            continue
        fetch_member(open_range, info, end, dest)
        fetched += info.compress_size
    return fetched


def with_retries(what, fn):
    for attempt in range(1, ATTEMPTS + 1):
        try:
            return fn()
        except (OSError, zipfile.BadZipFile, zlib.error) as exc:
            if attempt == ATTEMPTS:
                raise
            wait = 15 * attempt
            print(f"  {what}: {exc}; trying again in {wait} s", file=sys.stderr)
            time.sleep(wait)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, required=True, help="directory for the extracts")
    ap.add_argument("--regions", nargs="*", help="only these regions (default: all)")
    args = ap.parse_args()

    with urllib.request.urlopen(_request(INDEX_URL), timeout=TIMEOUT_S) as resp:
        extracts = conus_extracts(json.load(resp))
    if args.regions:
        unknown = sorted(set(args.regions) - set(extracts))
        if unknown:
            raise SystemExit(f"unknown regions: {', '.join(unknown)}")
        extracts = {r: extracts[r] for r in args.regions}

    args.out.mkdir(parents=True, exist_ok=True)
    sources_path = args.out / "sources.json"
    sources = json.loads(sources_path.read_text()) if sources_path.exists() else {}
    t0, total = time.time(), 0
    for n, (region, url) in enumerate(sorted(extracts.items()), start=1):
        # Keep reading the archive a partial download started from.
        dated = sources.get(region) or with_retries(region, lambda: resolve_dated(url))
        sources[region] = dated
        sources_path.write_text(json.dumps(sources, indent=2, sort_keys=True) + "\n")
        fetched = with_retries(
            region, lambda: fetch_layer(http_range(dated), args.out / region)
        )
        total += fetched
        print(
            f"[{n}/{len(extracts)}] {region}: "
            + (f"{fetched / 1e6:,.0f} MB" if fetched else "already complete")
            + f"  ({dated.rsplit('/', 1)[1]})",
            file=sys.stderr,
        )
    print(f"{total / 1e6:,.0f} MB in {time.time() - t0:,.0f} s", file=sys.stderr)


if __name__ == "__main__":
    main()
