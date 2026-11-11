# rb-road-network

**Rocky Branches Road Network Toolkit**: market area reports by road distance.

Give it a start point and a distance by road. It finds the area that can be
reached within that distance, lists the US counties the area touches, and
reports their population from 2010 to 2030 with the tons of material that
population implies.

The analysis runs in a Cloudflare Python Worker that reads its road, county
and population data from a D1 database. There are two ways to use it:

- **The map page**, served by the Worker: click a start point, run, and see
  the reachable area and the county table. It also runs batches from a CSV.
- **The command-line client** in this directory, which sends the same
  requests and saves the report files.

## Layout

| Path | What it is |
|---|---|
| `worker/` | The Worker: API, analysis engine, map page, D1 schema. See [worker/README.md](worker/README.md) for running, loading data and deploying. |
| `rb_road_network/` | The command-line client. |
| `tools/ingest/` | Local tools that turn road shapefiles, county boundaries and population CSVs into the SQL loaded into D1. |
| `scripts/` | Older helpers for downloading and converting source data. |
| `resources/` | QGIS styles, source lists and other reference files. |
| `output/` | Results from the earlier C++ program, kept for comparison. |

## Command-line client

Install it with [uv](https://docs.astral.sh/uv/) (plain `pip install .` also
works):

```bash
uv tool install .          # or: uv run rb-road-network ...
```

Point it at the Worker with `--url` or `RB_API_URL`. Without either it uses
`http://localhost:8787`, the local development server.

```bash
export RB_API_URL=https://rb-road-network.<your-subdomain>.workers.dev

rb-road-network status
rb-road-network run --lat 33.732 --lon -84.4166 --name Atlanta
rb-road-network batch --csv batch_inputs.csv
```

`run` prints the county table and saves three files, named after `--name`
(or the analysis id) in `output/`:

- `.tex`: the population table in LaTeX
- `.json`: the full result
- `.geojson`: the reachable area, in bands of road distance

Options: `-r/--radius` in metres (default 75000), `-t/--tons-per-person`
(default 4.5), `--min-km2` to leave out counties that are barely touched, and
`-f/--output` to choose where the `.tex` file goes.

`batch` takes a CSV with a header row `site, lat, lon`, runs every site, and
writes the same three files per site plus `batch_<id>_summary.csv` with one
line per site. Sites that cannot be analysed are reported and the command
exits with status 1. An interrupted batch continues with
`rb-road-network batch --resume <id>`; add `--retry-failed` to run the failed
sites again.

Every run is stored by the Worker, and each command prints a link that opens
it on the map page.

### If the Worker is behind Cloudflare Access

Create a service token in Cloudflare Zero Trust, allow it in the Worker's
Access policy (see [worker/README.md](worker/README.md#deploying)), and set:

```bash
export RB_ACCESS_CLIENT_ID=<client id>
export RB_ACCESS_CLIENT_SECRET=<client secret>
```

### Changes from the earlier CLI

The `--stride`, `--nthreads`, `--zoom`, `--no-exec`, `--yes`, `--rb-src` and
`--render` options are gone: they configured the local C++ program. `--lat`
and `--lon` are now required instead of prompted for. The PNG map is replaced
by the map page and the `.geojson` file.

## Development

```bash
# Command-line client tests
uv run --extra dev pytest

# Worker and ingest tests
cd worker && uv run pytest tests ../tools/ingest/tests
```

The ingest tools need `uv sync --extra ingest`. The helpers in `scripts/`
need `--extra scripts`, which includes GDAL and so needs the system GDAL
library. A plain `uv sync` removes both sets from `.venv`.

## The earlier C++ program

Until November 2026 the analysis was a C++ program (`justPop`) that read
shapefiles from a local data directory. Its source, build files and Docker
and Nix setup are no longer in the tree; the last commit that has them is
tagged `legacy-cpp`:

```bash
git checkout legacy-cpp
```

The Worker does not reproduce its numbers exactly, for two reasons:

- **The old algorithm was stochastic.** It traced many random walks along
  road cells from the start point, seeded from the clock, and marked every
  cell that any walk visited within the distance budget. Two runs with the
  same input could reach different cells, and so different counties. The
  Worker instead computes the shortest road distance to every cell and keeps
  all cells within the budget, so the same input always gives the same
  answer.
- **The old "radius" was applied as roughly twice the stated distance.**
  The Worker applies the distance as given.
