#!/usr/bin/env bash

set -e

# update_worker_deployment.sh

export REPO_ROOT
REPO_ROOT="$(realpath $(dirname $0)/..)"

cd "$REPO_ROOT/worker"
uv run pywrangler d1 migrations apply DB --remote                    # schema changes
uv run pywrangler d1 execute DB --remote --file "$REPO_ROOT/build/d1/roads.sql"   # new data
uv run pywrangler deploy                                              # code or map page
cd -
