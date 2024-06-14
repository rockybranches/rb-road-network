#!/usr/bin/env sh

docker image save qgis/qgis:latest > qgis_latest.tar

tar -Oxf qgis_latest.tar > temp.raw && qemu-img convert -f raw -O qcow2 temp.raw qgis_latest.qcow2 && rm temp.raw


