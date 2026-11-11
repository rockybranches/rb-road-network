# AI coding agent instructions for rb-road-network

Road-distance market area analysis: given a start point and a distance by
road, report the US counties reached and their population.

## Where things are

- `worker/` — Cloudflare Python Worker (API, analysis engine, map page) and
  its D1 schema. `worker/README.md` covers running, data loading and
  deploying. The engine in `worker/src/rbnet/` is pure standard-library
  Python with no Cloudflare imports, so it runs under ordinary pytest.
- `rb_road_network/` — command-line client of the Worker's API (Click plus
  the standard library; keep it free of other dependencies).
- `tools/ingest/` — local tools that build the SQL loaded into D1.
- `scripts/`, `resources/`, `output/` — older data helpers, reference files
  and results from the C++ program this replaced (tag `legacy-cpp`).

## Working here

- Worker and ingest tests: `cd worker && uv run pytest tests ../tools/ingest/tests`
- Client tests: `uv run --extra dev pytest` in the repo root
- In `worker/`, run `unset UV_PYTHON VIRTUAL_ENV` first; the root `.envrc`
  sets a relative `UV_PYTHON` that does not exist there.
- Runtime dependencies of the Worker must run in Pyodide; the list is empty
  on purpose.
- The API has no authentication of its own. Do not give the Worker a public
  address without Cloudflare Access in front of it.
