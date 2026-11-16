"""The detailed-result routes and queue consumer in entry.py.

entry.py needs the Workers runtime, so this replaces the `workers` module
with a stub and runs the Worker against fakes: D1 on sqlite3 with the real
migrations (so the SQL is checked for real), and in-memory R2 and Queue.
"""

import asyncio
import json
import sqlite3
import struct
import sys
import types
import zlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from rbnet import grid as g

MIGRATIONS = Path(__file__).resolve().parents[1] / "migrations"
T = g.TILE
TX, TY = 60, 40  # a tile near Columbus, Georgia


# -- stubs and fakes ---------------------------------------------------------


class _Response:
    def __init__(self, body=None, status=200, headers=None):
        self.body, self.status, self.headers = body, status, headers or {}

    def json(self):
        return json.loads(self.body)


class _Entrypoint:
    def __init__(self, ctx, env):
        self.ctx, self.env = ctx, env


@pytest.fixture(scope="module")
def entry():
    stub = types.ModuleType("workers")
    stub.Response = _Response
    stub.WorkerEntrypoint = _Entrypoint
    saved = sys.modules.get("workers")
    sys.modules["workers"] = stub
    sys.modules.pop("entry", None)
    try:
        import entry as module

        yield module
    finally:
        sys.modules.pop("entry", None)
        if saved is None:
            sys.modules.pop("workers", None)
        else:
            sys.modules["workers"] = saved


class _Stmt:
    def __init__(self, db, sql, args=()):
        self.db, self.sql, self.args = db, sql, args

    def bind(self, *args):
        return _Stmt(self.db, self.sql, args)

    def _execute(self):
        cur = self.db.execute(self.sql, self.args)
        names = [d[0] for d in cur.description or ()]
        return [SimpleNamespace(**dict(zip(names, row))) for row in cur.fetchall()]

    async def all(self):
        return SimpleNamespace(results=self._execute())

    async def first(self):
        rows = self._execute()
        return rows[0] if rows else None

    async def run(self):
        self._execute()
        self.db.commit()


class FakeD1:
    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        for path in sorted(MIGRATIONS.glob("*.sql")):
            self.db.executescript(path.read_text())

    def prepare(self, sql):
        return _Stmt(self.db, sql)


class FakeQueue:
    def __init__(self):
        self.sent = []

    async def sendBatch(self, messages):
        self.sent.extend(json.loads(m["body"]) for m in messages)


class FakeR2:
    def __init__(self):
        self.objects = {}

    async def put(self, key, value, options=None):
        self.objects[key] = value

    async def get(self, key):
        if key not in self.objects:
            return None
        return SimpleNamespace(body=self.objects[key])

    async def delete(self, keys):
        for key in keys:
            self.objects.pop(key, None)


class FakeMessage:
    def __init__(self, body, attempts=1):
        self.body, self.attempts = body, attempts
        self.outcome = None

    def ack(self):
        self.outcome = "ack"

    def retry(self):
        self.outcome = "retry"


def _env():
    db = FakeD1()
    # A road along row 50 of one tile, all of it in one county.
    roads = bytearray(T * T)
    for c in range(T):
        roads[50 * T + c] = 1
    counties = struct.pack(f"<{T * T}H", *([13215] * (T * T)))
    db.db.executemany(
        "INSERT INTO raster_tiles VALUES (?, ?, ?, ?, ?)",
        [
            ("osm-test", "roads", TY, TX, zlib.compress(bytes(roads))),
            ("tl-test", "counties", TY, TX, zlib.compress(counties)),
        ],
    )
    db.db.execute(
        "INSERT INTO counties VALUES (13215, 1, 'Muscogee', 'Muscogee County', "
        "'13', 'GA', 32.5, -84.9)"
    )
    db.db.executemany(
        "INSERT INTO county_population VALUES (13215, ?, ?, 'test')",
        [(y, 190000 + y) for y in range(2010, 2031, 5)],
    )
    db.db.commit()
    return SimpleNamespace(
        DB=db,
        ROADS_DATASET="osm-test",
        COUNTIES_DATASET="tl-test",
        DETAIL_QUEUE=FakeQueue(),
        DETAILS=FakeR2(),
    )


def _start():
    """A start point on the road, 60 cells into the tile."""
    lon, lat = g.xy_to_lonlat(*g.cell_center_xy(TX * T + 60, TY * T + 50))
    return {"lat": lat, "lon": lon, "radius_m": 2500, "label": "Columbus ext"}


class Harness:
    def __init__(self, entry):
        self.env = _env()
        self.worker = entry.Default(None, self.env)

    def call(self, method, path, body=None):
        async def text():
            return json.dumps(body)

        request = SimpleNamespace(
            url="http://localhost" + path, method=method, text=text
        )
        return asyncio.run(self.worker.fetch(request))

    def deliver(self, attempts=1):
        """Run the queue consumer on everything sent so far."""
        messages = [
            FakeMessage(json.dumps(job), attempts) for job in self.env.DETAIL_QUEUE.sent
        ]
        self.env.DETAIL_QUEUE.sent.clear()
        asyncio.run(self.worker.queue(SimpleNamespace(messages=messages)))
        return messages


@pytest.fixture
def h(entry):
    return Harness(entry)


# -- tests -------------------------------------------------------------------


def test_detail_is_built_in_the_background(h):
    created = h.call("POST", "/api/analyses", _start())
    assert created.status == 201, created.body
    aid = created.json()["id"]
    assert created.json()["detail"] is None

    # Not asked for yet.
    assert h.call("GET", f"/api/analyses/{aid}/detail.geojson").status == 409

    queued = h.call("POST", f"/api/analyses/{aid}/detail")
    assert queued.status == 202
    assert queued.json()["queued"] == 1
    assert queued.json()["analyses"][0]["detail"]["status"] == "queued"
    assert h.env.DETAIL_QUEUE.sent == [{"id": aid}]

    # Asking again while it waits does not queue it twice.
    assert h.call("POST", f"/api/analyses/{aid}/detail").json()["queued"] == 0
    assert len(h.env.DETAIL_QUEUE.sent) == 1

    pending = h.call("GET", f"/api/analyses/{aid}/detail.geojson")
    assert pending.status == 409
    assert "not ready" in pending.json()["error"]

    [message] = h.deliver()
    assert message.outcome == "ack"

    detail = h.call("GET", f"/api/analyses/{aid}/detail").json()["detail"]
    assert detail["status"] == "done"
    assert detail["points"] == 21
    assert detail["completed_at"]

    resp = h.call("GET", f"/api/analyses/{aid}/detail.geojson")
    assert resp.status == 200
    assert resp.headers["content-type"] == "application/geo+json"
    assert "Columbus_ext-detail.geojson" in resp.headers["content-disposition"]
    doc = json.loads(resp.body)
    assert [f["properties"]["name"] for f in doc["features"]] == [
        "StartPoint",
        "AccessibleArea",
    ]
    assert len(doc["features"][1]["geometry"]["coordinates"]) == 21
    assert detail["bytes"] == len(resp.body)

    # The full record carries the detail state too.
    assert h.call("GET", f"/api/analyses/{aid}").json()["detail"]["status"] == "done"

    # Done: asking again changes nothing.
    assert h.call("POST", f"/api/analyses/{aid}/detail").json()["queued"] == 0

    # Deleting the analysis deletes the file.
    assert h.call("DELETE", f"/api/analyses/{aid}").status == 200
    assert h.env.DETAILS.objects == {}


def test_detail_uses_the_datasets_of_the_stored_result(h):
    aid = h.call("POST", "/api/analyses", _start()).json()["id"]
    h.env.ROADS_DATASET = "osm-newer"  # not loaded; the detail must not use it
    h.call("POST", f"/api/analyses/{aid}/detail")
    h.deliver()
    detail = h.call("GET", f"/api/analyses/{aid}/detail").json()["detail"]
    assert detail["status"] == "done"


def test_analysis_error_fails_the_detail_without_retry(h):
    aid = h.call("POST", "/api/analyses", _start()).json()["id"]
    h.env.DB.db.execute("DELETE FROM raster_tiles WHERE layer = 'roads'")
    h.call("POST", f"/api/analyses/{aid}/detail")
    [message] = h.deliver()
    assert message.outcome == "ack"
    detail = h.call("GET", f"/api/analyses/{aid}/detail").json()["detail"]
    assert detail["status"] == "failed"
    assert "no road data" in detail["error"]
    resp = h.call("GET", f"/api/analyses/{aid}/detail.geojson")
    assert resp.status == 409
    assert "failed" in resp.json()["error"]

    # A failed detail can be asked for again.
    assert h.call("POST", f"/api/analyses/{aid}/detail").json()["queued"] == 1


def test_unexpected_error_is_retried_then_recorded(h, monkeypatch):
    aid = h.call("POST", "/api/analyses", _start()).json()["id"]
    h.call("POST", f"/api/analyses/{aid}/detail")

    async def broken(*args, **kwargs):
        raise RuntimeError("R2 is down")

    monkeypatch.setattr(h.env.DETAILS, "put", broken)
    job = list(h.env.DETAIL_QUEUE.sent)
    [first] = h.deliver(attempts=1)
    assert first.outcome == "retry"
    assert h.call("GET", f"/api/analyses/{aid}/detail").json()["detail"]["status"] == "running"

    h.env.DETAIL_QUEUE.sent.extend(job)
    [last] = h.deliver(attempts=3)
    assert last.outcome == "ack"
    detail = h.call("GET", f"/api/analyses/{aid}/detail").json()["detail"]
    assert detail["status"] == "failed"
    assert "internal error" in detail["error"]


def test_stale_job_is_queued_again(h):
    aid = h.call("POST", "/api/analyses", _start()).json()["id"]
    h.call("POST", f"/api/analyses/{aid}/detail")
    h.env.DETAIL_QUEUE.sent.clear()  # lost, as if killed at the CPU limit
    h.env.DB.db.execute(
        "UPDATE analyses SET detail_status = 'running', "
        "detail_requested_at = '2020-01-01T00:00:00+00:00'"
    )
    assert h.call("POST", f"/api/analyses/{aid}/detail").json()["queued"] == 1
    assert h.env.DETAIL_QUEUE.sent == [{"id": aid}]


def test_pending_analysis_has_no_detail(h):
    csv = "site,lat,lon\nA,{lat},{lon}\n".format(**_start())
    batch = h.call("POST", "/api/batches", {"csv": csv}).json()
    resp = h.call("POST", f"/api/batches/{batch['id']}/detail")
    assert resp.status == 409
    aid = batch["analyses"][0]["id"]
    assert h.call("POST", f"/api/analyses/{aid}/detail").status == 409


def test_batch_details_and_delete(h):
    start = _start()
    csv = "site,lat,lon\nA,{lat},{lon}\nB,{lat},{lon}\nC,10,10\n".format(**start)
    batch = h.call("POST", "/api/batches", {"csv": csv, "radius_m": 2500}).json()
    for row in batch["analyses"]:
        h.call("POST", f"/api/analyses/{row['id']}/run")

    resp = h.call("POST", f"/api/batches/{batch['id']}/detail")
    assert resp.status == 202
    assert resp.json()["queued"] == 2  # C failed, so it has no result
    h.deliver()
    rows = h.call("GET", f"/api/batches/{batch['id']}").json()["analyses"]
    assert [r["detail"] and r["detail"]["status"] for r in rows] == ["done", "done", None]
    assert len(h.env.DETAILS.objects) == 2

    h.call("DELETE", f"/api/batches/{batch['id']}")
    assert h.env.DETAILS.objects == {}


def test_message_for_a_deleted_analysis_is_dropped(h):
    aid = h.call("POST", "/api/analyses", _start()).json()["id"]
    h.call("POST", f"/api/analyses/{aid}/detail")
    h.call("DELETE", f"/api/analyses/{aid}")
    [message] = h.deliver()
    assert message.outcome == "ack"
    assert h.env.DETAILS.objects == {}


def test_malformed_message_is_dropped(h):
    message = FakeMessage("not json")
    asyncio.run(h.worker.queue(SimpleNamespace(messages=[message])))
    assert message.outcome == "ack"
