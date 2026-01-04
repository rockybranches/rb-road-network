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
	./scripts/backup-gis-osm-roads.sh
download-gis-osm-roads: backup-gis-osm-roads
	# download updated roads from geofabrik.de
	@echo -e "Downloading updated OSM data to '\${RB_DATA}/gis_osm_roads_downloads'..."
	./scripts/download-gis-osm-roads.sh

install_deps:
	./scripts/install_shapelib.sh

docker-compose-down:
	docker compose down --remove-orphans
docker-compose-build:
	docker compose build
docker-compose-up-force-rebuild:
	docker compose up --build --remove-orphans
docker-compose-up-daemon:
	docker compose up -d --remove-orphans
