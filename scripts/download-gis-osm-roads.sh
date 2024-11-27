#!/usr/bin/env bash

source ./.envrc
. ./scripts/_prebuild_setup.sh

echo "RB_SRC=${RB_SRC}"
echo "RB_DATA=${RB_DATA}"

source ./.venv/bin/activate

python -m pip install -r ./requirements.txt

python ./scripts/download-gis-osm-roads.py "$@"



