#!/usr/bin/env bash

source ./.envrc

echo "RB_SRC=${RB_SRC}"
echo "RB_DATA=${RB_DATA}"

aria2c --continue -j 10 -d ~/Documents/rb_data/gis_osm_roads_downloads -i $RB_SRC/resources/gis_osm_roads_updates.aria2
