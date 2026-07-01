#!/bin/bash
set -e

mkdir -p valhalla-data

echo "[INFO] Downloading Vietnam OSM PBF..."

wget -c -O valhalla-data/vietnam-260601.osm.pbf \
  https://download.geofabrik.de/asia/vietnam-260601.osm.pbf
echo "[INFO] Download completed."
ls -lh valhalla-data/vietnam-260601.osm.pbf

#echo "[INFO] Basic file info:"
#file valhalla-data/vietnam-260601.osm.pbf
#
#echo "[INFO] Osmium file info:"
#osmium fileinfo valhalla-data/vietnam-260601.osm.pbf
