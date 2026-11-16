#!/usr/bin/env bash

set -e

# run_worker_locally.sh

echo "starting rb-road-network worker locally..."

nohup /usr/bin/env bash -c " 
cd worker
unset UV_PYTHON VIRTUAL_ENV
uv sync
uv run pywrangler d1 migrations apply DB --local
for f in roads counties population; do
  uv run pywrangler d1 execute DB --local --file ../build/d1/$f.sql
done
uv run pywrangler dev
" &

