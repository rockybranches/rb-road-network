"""Tests for the command-line client, run against a stand-in for the Worker."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest
from click.testing import CliRunner

from rb_road_network.cli import _stem, cli
from rb_road_network.client import ApiError, Client

YEARS = [2010, 2015, 2020, 2025, 2030]


def _result(label):
    return {
        "request": {"label": label},
        "start": {"lat": 33.732, "lon": -84.4166, "moved_to_nearest_road": True},
        "reachable": {"km2": 1234.5},
        "warnings": ["Road data is not loaded for part of the search area."],
        "report": {
            "years": YEARS,
            "base_year": 2015,
            "target_year": 2030,
            "counties": [
                {"name": "Fulton", "state": "GA", "population": [1, 2000, 3, 4, 2500]},
                {"name": "DeKalb", "state": "GA", "population": [1, 1000, 3, 4, 1100]},
            ],
            "missing_population": [{"name": "Lost", "state": "VA"}],
            "totals": [2, 3000, 6, 8, 3600],
            "population_increase": 600,
            "percent_increase": 20.0,
            "tons_per_person": 4.5,
            "tons_base": 13500.0,
            "tons_target": 16200.0,
            "tons_increase": 2700.0,
        },
    }


class FakeWorker:
    """The parts of the API the client uses, held in memory."""

    def __init__(self):
        self.analyses = {}
        self.batches = {}
        self.requests = []  # (method, path, headers, body)
        self.fail_sites = set()  # labels whose run ends as 'failed'
        self.redirect_to = None

    def record(self, aid, full=False):
        a = self.analyses[aid]
        out = {
            "id": aid,
            "status": a["status"],
            "error": a.get("error"),
            "request": a["request"],
            "summary": None,
        }
        if a["status"] == "done":
            out["summary"] = {
                "counties": 2,
                "reached_km2": 1234.5,
                "population_base": 3000,
                "population_target": 3600,
            }
        if full:
            out["result"] = _result(a["request"]["label"]) if a["status"] == "done" else None
        return out

    def handle(self, method, path, body):
        parts = [p for p in path.split("/") if p]
        match (method, parts):
            case ("GET", ["api", "status"]):
                return 200, {
                    "ok": True,
                    "active": {"roads": "osm-test", "counties": "tl-test"},
                    "raster_tiles": [{"dataset": "osm-test", "layer": "roads", "tiles": 1500}],
                    "counties": 3108,
                    "counties_with_population": 3069,
                }
            case ("POST", ["api", "analyses"]):
                if not -90 < body["lat"] < 90:
                    return 400, {"error": "lat/lon out of range"}
                aid = f"a{len(self.analyses) + 1}"
                self.analyses[aid] = {"status": "done", "request": body}
                return 201, self.record(aid, full=True)
            case ("GET", ["api", "analyses", aid]) if aid in self.analyses:
                return 200, self.record(aid, full=True)
            case ("GET", ["api", "analyses", aid, "report.tex"]) if aid in self.analyses:
                return 200, "\\begin{tabular}\n"
            case ("GET", ["api", "analyses", aid, "area.geojson"]) if aid in self.analyses:
                return 200, '{"type": "FeatureCollection", "features": []}'
            case ("POST", ["api", "analyses", aid, "run"]) if aid in self.analyses:
                a = self.analyses[aid]
                if a["request"]["label"] in self.fail_sites:
                    a.update(status="failed", error="no road within reach of the start point")
                else:
                    a.update(status="done", error=None)
                return 200, self.record(aid)
            case ("POST", ["api", "batches"]):
                lines = [ln for ln in body["csv"].splitlines()[1:] if ln.strip()]
                bid = f"b{len(self.batches) + 1}"
                ids = []
                for line in lines:
                    site, lat, lon = line.split(",")
                    aid = f"a{len(self.analyses) + 1}"
                    self.analyses[aid] = {
                        "status": "pending",
                        "request": {"label": site, "lat": float(lat), "lon": float(lon)},
                    }
                    ids.append(aid)
                self.batches[bid] = {"label": body["label"], "ids": ids}
                return 201, self.batch(bid)
            case ("GET", ["api", "batches", bid]) if bid in self.batches:
                return 200, self.batch(bid)
            case ("GET", ["api", "batches", bid, "summary.csv"]) if bid in self.batches:
                return 200, "site,lat,lon\n"
        return 404, {"error": "not found"}

    def batch(self, bid):
        b = self.batches[bid]
        return {"id": bid, "label": b["label"], "analyses": [self.record(a) for a in b["ids"]]}


@pytest.fixture
def worker():
    fake = FakeWorker()

    class Handler(BaseHTTPRequestHandler):
        def _serve(self):
            length = int(self.headers.get("content-length") or 0)
            body = json.loads(self.rfile.read(length)) if length else None
            fake.requests.append((self.command, self.path, dict(self.headers), body))
            if fake.redirect_to:
                self.send_response(302)
                self.send_header("location", fake.redirect_to)
                self.end_headers()
                return
            status, payload = fake.handle(self.command, self.path, body)
            data = (payload if isinstance(payload, str) else json.dumps(payload)).encode()
            self.send_response(status)
            self.send_header("content-length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        do_GET = do_POST = _serve

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    ).start()
    fake.url = f"http://127.0.0.1:{server.server_port}"
    yield fake
    server.shutdown()
    server.server_close()


def invoke(worker, *args):
    return CliRunner().invoke(cli, ["--url", worker.url, *args])


def test_status(worker):
    result = invoke(worker, "status")
    assert result.exit_code == 0, result.output
    assert "osm-test / roads: 1,500 tiles" in result.output
    assert "3,069 with population figures" in result.output


def test_run_prints_the_table_and_saves_three_files(worker, tmp_path):
    out = tmp_path / "reports" / "atlanta.tex"
    result = invoke(
        worker, "run", "--lat", "33.732", "--lon", "-84.4166", "-r", "50000",
        "-t", "5", "--name", "Atlanta", "-f", str(out),
    )  # fmt: skip
    assert result.exit_code == 0, result.output
    sent = worker.requests[0][3]
    assert sent == {
        "lat": 33.732, "lon": -84.4166, "radius_m": 50000.0,
        "tons_per_person": 5.0, "min_km2": 0.0, "label": "Atlanta",
    }  # fmt: skip
    assert "Fulton" in result.output and "3,600" in result.output
    assert "600 more people (20.0%)" in result.output
    assert "Start point moved to the nearest road" in result.output
    assert "Road data is not loaded" in result.output
    assert "Lost, VA" in result.output
    assert f"Map: {worker.url}/#a/a1" in result.output
    assert out.read_text().startswith("\\begin{tabular}")
    assert json.loads(out.with_suffix(".json").read_text())["id"] == "a1"
    assert json.loads(out.with_suffix(".geojson").read_text())["type"] == "FeatureCollection"


def test_run_default_output_is_named_after_the_site(worker, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = invoke(worker, "run", "--lat", "33", "--lon", "-84", "--name", "Pigeon Point/2")
    assert result.exit_code == 0, result.output
    assert (tmp_path / "output" / "Pigeon_Point_2.tex").exists()


def test_run_reports_the_workers_error(worker, tmp_path):
    result = invoke(worker, "run", "--lat", "95", "--lon", "-84", "-f", str(tmp_path / "x.tex"))
    assert result.exit_code == 1
    assert "Error: lat/lon out of range" in result.output
    assert not (tmp_path / "x.tex").exists()


def test_batch_runs_every_site_and_writes_the_summary(worker, tmp_path):
    sites = tmp_path / "sites.csv"
    sites.write_text("site,lat,lon\nSavannah,32.07,-81.10\nNowhere,30.0,-80.0\nAtlanta,33.7,-84.4\n")
    worker.fail_sites.add("Nowhere")
    out = tmp_path / "out"
    result = invoke(worker, "batch", "--csv", str(sites), "-o", str(out))
    assert result.exit_code == 1  # one site failed
    assert "Batch b1 (sites): 3 site(s)" in result.output
    assert "[1/3] Savannah: 2 counties, 3,000 to 3,600 people" in result.output
    assert "[2/3] Nowhere: failed: no road within reach" in result.output
    assert "1 site(s) failed." in result.output
    assert sorted(p.name for p in out.iterdir()) == [
        "Atlanta.geojson", "Atlanta.json", "Atlanta.tex",
        "Savannah.geojson", "Savannah.json", "Savannah.tex",
        "batch_b1_summary.csv",
    ]  # fmt: skip
    # The saved result is the full record, not the summary the run returns.
    assert "report" in json.loads((out / "Savannah.json").read_text())["result"]
    created = worker.requests[0][3]
    assert created["radius_m"] == 75000 and created["csv"].startswith("site,lat,lon")


def test_batch_resume_runs_only_what_is_left(worker, tmp_path):
    sites = tmp_path / "sites.csv"
    sites.write_text("site,lat,lon\nA,32,-81\nB,33,-84\n")
    worker.fail_sites.add("B")
    assert invoke(worker, "batch", "--csv", str(sites), "-o", str(tmp_path)).exit_code == 1

    def runs():
        return [path for method, path, _, _ in worker.requests if path.endswith("/run")]

    worker.requests.clear()
    result = invoke(worker, "batch", "--resume", "b1", "-o", str(tmp_path))
    assert result.exit_code == 1 and runs() == []  # failed sites are left alone

    worker.fail_sites.clear()
    result = invoke(worker, "batch", "--resume", "b1", "--retry-failed", "-o", str(tmp_path))
    assert result.exit_code == 0, result.output
    assert runs() == ["/api/analyses/a2/run"]
    assert (tmp_path / "B.tex").exists()


def test_batch_gives_sites_with_the_same_name_separate_files(worker, tmp_path):
    sites = tmp_path / "sites.csv"
    sites.write_text("site,lat,lon\nPit,32,-81\nPit,33,-84\n,34,-85\n")
    result = invoke(worker, "batch", "--csv", str(sites), "-o", str(tmp_path / "out"))
    assert result.exit_code == 0, result.output
    names = {p.stem for p in (tmp_path / "out").glob("*.tex")}
    assert names == {"Pit", "Pit_2", "site_3"}


def test_batch_needs_exactly_one_of_csv_and_resume(worker, tmp_path):
    assert invoke(worker, "batch").exit_code == 2
    sites = tmp_path / "sites.csv"
    sites.write_text("site,lat,lon\n")
    assert invoke(worker, "batch", "--csv", str(sites), "--resume", "b1").exit_code == 2


def test_unknown_batch(worker):
    result = invoke(worker, "batch", "--resume", "nope")
    assert result.exit_code == 1 and "not found" in result.output


def test_access_service_token_is_sent(worker, monkeypatch):
    monkeypatch.setenv("RB_ACCESS_CLIENT_ID", "abc.access")
    monkeypatch.setenv("RB_ACCESS_CLIENT_SECRET", "s3cret")
    assert invoke(worker, "status").exit_code == 0
    headers = {k.lower(): v for k, v in worker.requests[0][2].items()}
    assert headers["cf-access-client-id"] == "abc.access"
    assert headers["cf-access-client-secret"] == "s3cret"
    assert headers["user-agent"] == "rb-road-network-cli"


def test_access_login_redirect_is_explained(worker):
    worker.redirect_to = "https://team.cloudflareaccess.com/cdn-cgi/access/login/x"
    result = invoke(worker, "status")
    assert result.exit_code == 1
    assert "behind Cloudflare Access" in result.output
    assert "RB_ACCESS_CLIENT_ID" in result.output


def test_unreachable_worker():
    result = CliRunner().invoke(cli, ["--url", "http://127.0.0.1:9", "status"])
    assert result.exit_code == 1 and "could not reach http://127.0.0.1:9" in result.output


def test_url_from_environment(worker, monkeypatch):
    monkeypatch.setenv("RB_API_URL", worker.url + "/")
    result = CliRunner().invoke(cli, ["status"])
    assert result.exit_code == 0 and f"Worker: {worker.url}\n" in result.output


def test_non_json_answer():
    client = Client("http://127.0.0.1:9")
    client._request = lambda *a: "<html>"
    with pytest.raises(ApiError, match="did not answer with JSON"):
        client.status()


@pytest.mark.parametrize(
    "label, expected",
    [("Diggs South Sand", "Diggs_South_Sand"), ("../../etc/passwd", "etc_passwd"), ("", "x"), ("...", "x")],
)
def test_stem(label, expected):
    assert _stem(label, "x") == expected
