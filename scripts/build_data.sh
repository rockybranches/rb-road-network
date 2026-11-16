#!/usr/bin/env bash

set -e

# build_data.sh

uv sync --extra ingest
PY="uv run python"
COUNTIES="$RB_DATA"/tl_2016_us_county/tl_2016_us_county.shp
ROADS="$RB_DATA"/gis_osm_roads_2026-11

# Download the roads layer of every state extract from Geofabrik: 50
# archives, about 7 GB fetched and 20 GB on disk. It reads only the roads
# files out of each archive, and can be run again after an interruption.
$PY tools/ingest/fetch_roads.py --out "$ROADS"

# Roads: pass every state extract for one dataset in a single run.
# --counties marks roadless tiles (open water, wilderness) in those states
# as loaded, so the Worker does not warn that data is missing there.
$PY tools/ingest/rasterize_roads.py "$ROADS"/*/gis_osm_roads_free_1.shp \
  --counties "$COUNTIES" --dataset osm-2026-11 --sql build/d1/roads.sql

# County boundaries and attributes (contiguous US).
$PY tools/ingest/rasterize_counties.py "$COUNTIES" \
  --dataset tl-2016 --sql build/d1/counties.sql

# Population. Prints which rows it corrected or could not place.
$PY tools/ingest/load_population.py \
  --counties "$COUNTIES" --csv-dir "$RB_DATA"/county_pop \
  --source county-pop-reconciled-2026-11 --sql build/d1/population.sql
