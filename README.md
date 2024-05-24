# rb-road-network

*last update: 2023-01-22*

### Rocky Branches - Road Network Toolkit

## Usage - Docker

(after setting environment variables, listed below)

1) Build the docker image.

`$ ./docker_build.sh`

2) Run the interactive tool.

`$ ./docker_run.sh`

## Summary

GIS toolkit for creating market area reports, including:
- US county demographics
- Road-distance market area maps


## Compatibility

*Tested on:*
- Arch Linux
- Debian 10
- Ubuntu

- - -


## Dependencies

### Packages

- *shapelib (1.5)*
  - libshp-dev
- libcairo-dev [optional]
- libosmium-dev [optional]
- libgtk+-3 [optional]
- docker-desktop (for `docker` usage)
  - [Install on Debian](https://docs.docker.com/desktop/install/debian/)

- - -

## How to build

### Setup

#### Environment variables

```bash

# absolute path of source/repo directory 
#  (also contains executables)

export RB_SRC=$HOME/Git/rb-road-network 


# path for resources

export XDG_DATA_DIRS=$RB_PATH/share/


# absolute path of data, 
# e.g. .SHP road map files

export RB_DATA=$HOME/Documents/rb_data

```

- - -

### Linux

```bash
$ src=justPop exe=justPop make arch=linux
```

### Windows

```bash
$ src=justPop exe=justPop make arch=win
```

- - -


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

### Update county population data from Google Drive CSVs (Multi-step)

#### (1) Download US county population data from Google Drive (latest)

```bash
$ $RB_SRC/scripts/downloadCountyPop/downloadCountyPop.sh
```

#### (2) Update local geo-ref data file (CSV -> DBF)

**(2.1) Build**

```bash
$ $RB_SRC/scripts/build_scripts.sh
```

**(2.2) Update**

*`$RB_DATA/county_pop/CSVs` -> `$RB_DATA/tl_2016_us_county_wgs84/tl_2016_us_county.dbf`*

```bash
$> $RB_SRC/scripts/build_scripts.sh
$> $RB_SRC/scripts/bin/countyPop2DBF.exe
```

**Download $RB_DATA**
```bash
$> $RB_SRC/scripts/download_rb_data.sh
$> $RB_SRC/scripts/downloadCountyPop.sh
```

**Docker**

```bash
$> $RB_SRC/docker_build.sh && $RB_SRC/docker_run.sh
```

**Interactive script**
```bash
$> $RB_SRC/scripts/roads_rb
```

- - -


## Troubleshooting

### "undefined reference" when using experimental filesystem...

#### Make sure to use gnu++17 (or later) `-std=gnu++2a` & link experimental fs

```bash
$ g++ -std=gnu++2a *.cpp -lstdc++fs
```

ref: https://stackoverflow.com/questions/49249349/undefined-reference-when-using-experimental-filesystem/49250698#49250698
