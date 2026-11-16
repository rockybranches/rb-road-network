#!/usr/bin/env bash

set -e

# run_worker_locally.sh

echo "starting rb-road-network worker locally..."

export REPO_ROOT="$(realpath $(dirname $0)/..)"

cd worker
unset UV_PYTHON VIRTUAL_ENV
uv sync
uv run pywrangler d1 migrations apply DB --local
for f in roads counties population; do
  uv run pywrangler d1 execute DB --local --file "$REPO_ROOT/build/d1/$f.sql"
done
uv run pywrangler dev

