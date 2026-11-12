"""Tests for fetch_roads: region selection and ranged reads of an archive."""

import io
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import fetch_roads  # noqa: E402


def _feature(region, iso=None, parent="north-america", shp=True):
    urls = {"pbf": f"https://example.test/{region}.osm.pbf"}
    if shp:
        urls["shp"] = f"https://example.test/{region}-latest-free.shp.zip"
    props = {"id": region, "parent": parent, "urls": urls}
    if iso:
        props["iso3166-2"] = [iso]
    return {"properties": props}


def test_conus_extracts_skips_other_places_and_splits_california():
    index = {
        "features": [
            _feature("us/georgia", "US-GA"),
            _feature("us/alaska", "US-AK"),
            _feature("us/puerto-rico", "US-PR"),
            _feature("georgia", "GE", parent="asia"),
            _feature("us/california", "US-CA", shp=False),
            _feature("norcal", parent="us/california"),
            _feature("socal", parent="us/california"),
        ]
    }
    extracts = fetch_roads.conus_extracts(index)
    assert sorted(extracts) == ["georgia", "norcal", "socal"]
    assert extracts["georgia"] == "https://example.test/us/georgia-latest-free.shp.zip"


def test_conus_extracts_fails_when_a_state_has_no_archive():
    with pytest.raises(SystemExit):
        fetch_roads.conus_extracts({"features": [_feature("us/texas", "US-TX", shp=False)]})


class _Response(io.BytesIO):
    def __init__(self, data, start, total):
        super().__init__(data)
        self.headers = {"content-range": f"bytes {start}-{start + len(data) - 1}/{total}"}


class FakeArchive:
    """Serves ranges of an in-memory zip and records what was asked for."""

    def __init__(self, files, damage=None):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for name, (data, method) in files.items():
                zf.writestr(name, data, compress_type=method)
        self.data = bytearray(buf.getvalue())
        if damage:
            at = self.data.find(damage)
            self.data[at] ^= 0xFF
        self.requests = []

    def open_range(self, start, end=None):
        total = len(self.data)
        if end is None:
            start = max(0, total + start)
            end = total - 1
        self.requests.append((start, end))
        return _Response(bytes(self.data[start : end + 1]), start, total)


ROADS = {
    "gis_osm_roads_free_1.shp": (b"shape" * 5000, zipfile.ZIP_DEFLATED),
    "gis_osm_roads_free_1.dbf": (b"fclass" * 3000, zipfile.ZIP_DEFLATED),
    "gis_osm_roads_free_1.cpg": (b"UTF-8", zipfile.ZIP_STORED),
}
OTHER = {
    "gis_osm_buildings_a_free_1.shp": (bytes(range(256)) * 400, zipfile.ZIP_STORED),
    "gis_osm_railways_free_1.shp": (b"rail" * 100, zipfile.ZIP_DEFLATED),
}


def test_fetch_layer_downloads_only_the_roads_files(tmp_path):
    files = {**OTHER, **ROADS}
    files = dict(sorted(files.items(), key=lambda kv: kv[0][-5:]))  # interleave
    archive = FakeArchive(files)
    fetch_roads.fetch_layer(archive.open_range, tmp_path / "ga")

    assert sorted(p.name for p in (tmp_path / "ga").iterdir()) == sorted(ROADS)
    for name, (data, _) in ROADS.items():
        assert (tmp_path / "ga" / name).read_bytes() == data
    # One request for the file list, one per roads file, none for the rest.
    assert len(archive.requests) == 1 + len(ROADS)
    buildings = len(OTHER["gis_osm_buildings_a_free_1.shp"][0])
    assert sum(end - start + 1 for start, end in archive.requests[1:]) < buildings


def test_fetch_layer_skips_files_that_are_already_complete(tmp_path):
    archive = FakeArchive(ROADS)
    fetch_roads.fetch_layer(archive.open_range, tmp_path)
    (tmp_path / "gis_osm_roads_free_1.dbf").write_bytes(b"cut short")
    archive.requests.clear()
    fetched = fetch_roads.fetch_layer(archive.open_range, tmp_path)

    assert len(archive.requests) == 2  # the file list and the damaged file
    assert fetched > 0
    assert (tmp_path / "gis_osm_roads_free_1.dbf").read_bytes() == ROADS[
        "gis_osm_roads_free_1.dbf"
    ][0]


def test_fetch_layer_rejects_a_corrupted_file(tmp_path):
    archive = FakeArchive(ROADS, damage=b"UTF-8")
    with pytest.raises(OSError, match="checksum"):
        fetch_roads.fetch_layer(archive.open_range, tmp_path)
    assert not (tmp_path / "gis_osm_roads_free_1.cpg").exists()
    assert not list(tmp_path.glob("*.part"))


def test_fetch_layer_needs_the_shapefile(tmp_path):
    archive = FakeArchive(OTHER)
    with pytest.raises(OSError, match="no gis_osm_roads_free_1.shp"):
        fetch_roads.fetch_layer(archive.open_range, tmp_path)
