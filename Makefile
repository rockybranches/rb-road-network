arch ?= linux
src ?= justPop
exe ?= justPop
RB_DEBUG ?= true
THRUST_RB ?= false
INCLUDE ?= $(realpath -ms $(RB_SRC)/include/)

.PHONY: help
help:  ## Display this help screen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-32s\033[0m %s\n", $$1, $$2}'

.PHONY: clean build test debug

test:  ## Clean, then build and run ${src} as ${exe} for ${arch}
	$(MAKE) -ke clean
	./build.sh ${src} ${exe} ${arch}
build:  ## Clean, then build ${src} as ${exe} for ${arch}
	$(MAKE) -ke clean
	./build.sh ${src} ${exe} ${arch}
build_thrust:  ## Clean, then build and run the Thrust test (testThrust)
	$(MAKE) -ke clean
	THRUST_RB=true src=testThrust exe=testThrust $(MAKE) -ke test
debug:  ## Clean, then build and run with RB_DEBUG=true
	$(MAKE) -ke clean
	RB_DEBUG=true $(MAKE) -ke test
clean:  ## Remove emacs backup files and object files in RB_SRC
	# clean emacs backup files
	find . -type f -name '*~' -exec rm {} \;
	# clean object files
	rm $(RB_SRC)/*.o || echo "nothing to clean\n"

backup-gis-osm-roads:  ## Back up existing GIS OSM roads data
	./scripts/backup-gis-osm-roads.sh
download-gis-osm-roads: backup-gis-osm-roads  ## Back up, then download updated OSM roads from geofabrik.de
	# download updated roads from geofabrik.de
	@echo -e "Downloading updated OSM data to '\${RB_DATA}/gis_osm_roads_downloads'..."
	./scripts/download-gis-osm-roads.sh

install_deps:  ## Install dependencies (shapelib)
	./scripts/install_shapelib.sh

docker-compose-down:  ## Stop containers and remove orphans
	docker compose down --remove-orphans
docker-compose-build:  ## Build docker compose images
	docker compose build
docker-compose-up-force-rebuild:  ## Rebuild images and start containers in the foreground
	docker compose up --build --remove-orphans
docker-compose-up-daemon:  ## Start containers in the background
	docker compose up -d --remove-orphans
