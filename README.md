# rb-road-network

### Rocky Branches - Road Network Toolkit

## Usage - Docker Compose

**current ~ October 15, 2024**

```bash

docker compose run rb-roads

```

## Usage - Docker

(after setting environment variables, listed below)

1. Build the docker image.

`$ ./docker_build.sh`

1. Run the interactive tool.

`$ ./docker_run.sh`

## Summary

GIS toolkit for creating market area reports, including:

- US county demographics
- Road-distance market area maps

## Compatibility

_Tested on:_

- Arch Linux
- Debian 10
- Ubuntu

---

## Dependencies

### Packages

- _shapelib (1.5)_
  - libshp-dev
- libcairo-dev [optional]
- libosmium-dev [optional]
- libgtk+-3 [optional]
- docker-desktop (for `docker` usage)
  - [Install on Debian](https://docs.docker.com/desktop/install/debian/)

---

## How to build

### Setup

#### Environment variables

Use `direnv` to manage environment variables (`./.envrc` defines the following):

```bash
# absolute path of source/repo directory
#  (also contains executables)
export RB_SRC=$HOME/Git/rb-road-network
export RB_PATH=$RB_SRC

# path for resources
export XDG_DATA_DIRS=$RB_PATH/share/

# absolute path of data,
# e.g. .SHP road map files
export RB_DATA=$HOME/Documents/rb_data
```

#### Build

### Linux

```bash
src=justPop exe=justPop make arch=linux
```

### Windows

```bash
src=justPop exe=justPop make arch=win
```

---

## Examples

### Make a poptable

```bash
# `--radius` should be given in meters!
$ ./justPop.exe \
 -f ./output/justPopResult.txt \
 --lat=30.2 --lon=-83.0 \
 --radius=75000 \
 --stride=0.009 \
 --tons-per-person=4.5 \
 --nthreads=8 \
 --zoom=0.5
```

### Download new roads data (shapefiles)

```bash
$ ./scripts/download_gis_osm_roads.sh
```

### Update county population data from Google Drive CSVs (Multi-step)

#### (1) Download US county population data from Google Drive (latest)

```bash
$RB_SRC/scripts/downloadCountyPop/downloadCountyPop.sh

```

#### (2) Update local geo-ref data file (CSV -> DBF)

*(2.1) Build*

```bash
$RB_SRC/scripts/build_scripts.sh
```

*(2.2) Update*

_`$RB_DATA/county_pop/CSVs` -> `$RB_DATA/tl_2016_us_county_wgs84/tl_2016_us_county.dbf`_

```bash
$> $RB_SRC/scripts/build_scripts.sh
$> $RB_SRC/scripts/bin/countyPop2DBF.exe
```

*Download $RB_DATA*

```bash
$> $RB_SRC/scripts/download_rb_data.sh
$> $RB_SRC/scripts/downloadCountyPop.sh
```

*Docker*

```bash
$> $RB_SRC/docker_build.sh && $RB_SRC/docker_run.sh
```

*Interactive script*

```bash
$> $RB_SRC/scripts/roads_rb
```

---

## Troubleshooting

### 'how to copy a file from a running docker container to local?'

#### Quick example

```bash

# for running container 'rb-road-network-rb-roads-run-77c22bf4c6b1'
$ docker cp rb-road-network-rb-roads-run-77c22bf4c6b1:/home/appuser/rb_app/SpanishCut.json ./

```

To copy a file from a running Docker container to your local filesystem, you can use
the docker cp command. Here's a step-by-step guide to doing that:

1. First, identify the container ID or name of the running container. You can list all
   running containers with the command:

`docker ps`

1. Determine the full path of the file you want to copy from the container.
2. Use the docker cp command to copy the file from the container to your local
   machine. The format for the command is as follows:

`docker cp <container_id_or_name>:<container_file_path> <local_target_path>`

Here's an example use case:

Let's say you have a container named my_container , and you want to copy a file
/tmp/example.txt from the container to your local directory /home/user/ .

You would run:

`docker cp my_container:/tmp/example.txt /home/user/`

After this command runs successfully, the file example.txt should be present on your
local filesystem in /home/user/ .

Please make sure you have appropriate permissions to access the targeted directory on
your local filesystem, and take note that if a file with the same name already exists
at the local path, it will be overwritten by default.

### **Error:** `No data was available for the requested area`

#### Did you make sure to use the correct sign for the **longitude**?

**Recall:** West longitude should be given as negative (e.g., `81.0W` means `-81.0`)

### **Error:** `"undefined reference" when using experimental filesystem...`

#### Make sure to use gnu++17 (or later) `-std=gnu++2a` & link experimental fs

```bash
g++ -std=gnu++2a *.cpp -lstdc++fs
```

ref: <https://stackoverflow.com/questions/49249349/undefined-reference-when-using-experimental-filesystem/49250698#49250698>
