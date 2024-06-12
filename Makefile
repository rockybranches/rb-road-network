arch ?= linux
src ?= justPop
exe ?= justPop
RB_DEBUG ?= false
THRUST_RB ?= false
INCLUDE ?= $(realpath -ms $(RB_SRC)/include/)
.PHONY: clean build test debug

build:
	$(MAKE) -ke clean
	./build.sh ${src} ${exe} ${arch}
test:
	$(MAKE) -ke clean
	./build.sh ${src} ${src} ${arch}
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

docker-compose-down:
	docker compose down --remove-orphans
docker-compose-build:
	docker compose build
docker-compose-up-force-rebuild:
	docker compose up --build --remove-orphans
docker-compose-up-daemon:
	docker compose up -d --remove-orphans