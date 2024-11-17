#!/usr/bin/env bash

read -p "Continue to backup ${RB_DATA}/gis_osm_roads_extra? [y]/n: " -ei "y" contflag
if [ $contflag == "y" ];
then
       # backup current roads files
       echo -e "Backing up gis_osm_roads_extra..."
       tar --use-compress-program=pbzip2 -cf ${RB_DATA}/gis_osm_roads_extra_backup.tar.bz2 ${RB_DATA}/gis_osm_roads_extra
       echo -e "...done."
else
       echo -e "ok, skipping backup then... :)"
fi
