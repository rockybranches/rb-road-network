# Changelog

All notable changes to **rb-road-network** are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- **`rb-road-network batch` CLI subcommand** — reads a CSV file (columns: `site`, `lat`, `lon`)
  and runs `justPop.exe` for every row, saving per-site result files to an output directory.
- **Automatic Plotly map rendering** — after each `run` or `batch` computation, the CLI
  invokes `render_scripts/render_plotly.py` to produce a PNG map alongside the text output.
  Rendering can be suppressed with `--no-render`.
- **`render_plotly.py --output` flag** — the Plotly render script now accepts `-o / --output`
  to save the figure to a PNG file instead of opening a browser window.
- **CLI test suite** (`tests/test_cli.py`) — pytest-based tests covering:
  - `--no-exec` smoke tests for `run` and `batch`
  - Mock-subprocess tests for command construction and execution
  - Edge cases: missing executable, bad CSV columns, special characters in site names
- **`pyproject.toml` dev extras** — `pytest` is now listed under `[project.optional-dependencies] dev`.

### Fixed
- **`include/utils.hpp` — missing null-check after `SHPOpen()` (line 697)**
  Added a null-check with a descriptive warning; the loop iteration is skipped when a
  shapefile cannot be opened instead of crashing with a null-pointer dereference.
- **`include/utils.hpp` — missing null-check after `SHPOpen()` (line 748)**
  Same fix applied to the secondary shapefile load loop.
- **`include/utils.hpp` — missing `gis_extra_path` existence check**
  A `std::runtime_error` is now raised with an informative message when the
  `gis_osm_roads_extra/` directory does not exist.
- **`include/utils.hpp` — empty `shapefn` not validated**
  After the directory scan, an explicit check throws `std::runtime_error` when no
  primary roads shapefile was matched for the requested area.
- **`include/places.hpp` — missing null-check after `SHPOpen()` for county shapefile**
  `loadCountySHP` now throws `std::runtime_error` with the file path when the shapefile
  cannot be opened.
- **`include/places.hpp` — missing null-check after `SHPOpen()` for states shapefile**
  `States::States()` now throws `std::runtime_error` when the states shapefile cannot
  be opened.
- **`src/justPop.cc` — missing `break` in `switch` case `'f'`**
  The `-f` / `--output-file-path` case previously fell through to `case '?'`. The missing
  `break` statement has been added.

### Changed
- **`pyproject.toml` description** updated from placeholder to a meaningful summary.

---

## [0.1.0] — 2026-03-17

### Added
- Initial Python CLI (`rb-road-network run`) wrapping `justPop.exe` via Click.
- `pyproject.toml` entry-point registration for `rb-road-network`.
- README updated with Python CLI usage instructions.

## [0.0.1] — 2026-02-22

### Added
- Initial commit: C++ source (`justPop`, `roadsrb`, etc.), Python scripts, Docker Compose,
  Nix flake, QGIS styles, GDB configs, and CI configuration.
