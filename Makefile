arch ?= linux
src ?= justPop
exe ?= justPop
RB_DEBUG ?= true
THRUST_RB ?= false
INCLUDE ?= $(realpath -ms $(RB_SRC)/include/)

.PHONY: clean build test debug

test:
	$(MAKE) -ke clean
	./build.sh ${src} ${exe} ${arch}
build:
	$(MAKE) -ke clean
	./build.sh ${src} ${exe} ${arch}
build_thrust:
	$(MAKE) -ke clean
	THRUST_RB=true src=testThrust exe=testThrust $(MAKE) -ke test
debug:
	$(MAKE) -ke clean
	RB_DEBUG=true $(MAKE) -ke test
clean:
	# clean emacs backup files
	find . -type f -name '*~' -exec rm {} \;
	# clean object files
	rm $(RB_SRC)/*.o || echo "nothing to clean\n"

backup-gis-osm-roads:
	# backup current roads files
	@echo -e "Backing up gis_osm_roads_extra..."
	tar --use-compress-program=pbzip2 -cf $(RB_DATA)/gis_osm_roads_extra_backup.tar.bz2 $(RB_DATA)/gis_osm_roads_extra

download-gis-osm-roads: backup-gis-osm-roads
	# download updated roads from geofabrik.de
	@echo -e "Downloading updated OSM data to '\${RB_DATA}/gis_osm_roads_downloads'..."
	aria2c --continue -j 10 -d $(realpath $(RB_DATA)/gis_osm_roads_downloads) -i $(RB_SRC)/resources/gis_osm_roads_updates.aria2
	# unzip updated roads
	@echo -e "Unzipping updated gis_osm_roads_extra..."
	unzip $(RB_DATA)/gis_osm_roads_downloads/*.zip -d $(RB_DATA)/gis_osm_roads/
	@echo -e "...done."

docker-compose-down:
	docker compose down --remove-orphans
docker-compose-build:
	docker compose build
docker-compose-up-force-rebuild:
	docker compose up --build --remove-orphans
docker-compose-up-daemon:
	docker compose up -d --remove-orphans