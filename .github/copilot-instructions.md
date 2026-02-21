# AI Coding Agent Instructions for rb-road-network

Welcome to the **rb-road-network** project! This document provides essential guidelines for AI coding agents to be productive in this codebase. The project is a GIS toolkit for creating market area reports, with a focus on road-distance analysis and demographic data visualization.

## Project Overview

- **Core Components:**
  - **C++ executables:** Perform road network computations (e.g., `justPop`).
  - **Python scripts:** Handle data processing and visualization (e.g., `render_plotly.py`).
  - **Docker:** Provides a containerized environment for execution.
  - **GIS tools:** Utilizes GDAL/OGR, shapelib, and QGIS for geospatial operations.
- **Data Flow:**
  1. Input: Latitude/longitude coordinates and radius.
  2. Processing: Road network analysis to determine reachable areas.
  3. Output: Population estimates and market area maps.

## Developer Workflows

### Building the Project

- **Linux:**
  ```bash
  src=justPop exe=justPop make arch=linux
  ```
- **Windows:**
  ```bash
  src=justPop exe=justPop make arch=win
  ```
- **Docker:**
  ```bash
  ./docker_build.sh && ./docker_run.sh
  ```

### Running Key Scripts

- **Generate Population Table:**
  ```bash
  ./justPop.exe \
   -f ./output/justPopResult.txt \
   --lat=30.2 --lon=-83.0 \
   --radius=75000 \
   --stride=0.009 \
   --tons-per-person=4.5 \
   --nthreads=8 \
   --zoom=0.5
  ```
- **Download Roads Data:**
  ```bash
  ./scripts/download_gis_osm_roads.sh
  ```
- **Update County Population Data:**
  1. Download data:
     ```bash
     ./scripts/downloadCountyPop/downloadCountyPop.sh
     ```
  2. Build and update:
     ```bash
     ./scripts/build_scripts.sh
     ./scripts/bin/countyPop2DBF.exe
     ```

### Environment Setup

- Use `direnv` to manage environment variables. Key variables include:
  ```bash
  export RB_SRC=$HOME/Git/rb-road-network
  export RB_PATH=$RB_SRC
  export XDG_DATA_DIRS=$RB_PATH/share/
  export RB_DATA=$HOME/Documents/rb_data
  ```

## Project-Specific Conventions

- **C++ Code:**
  - Header files are in `include/`.
  - Source files are in `src/`.
  - Follow modular design principles; each `.cc` file corresponds to a specific functionality.
- **Python Scripts:**
  - Located in `scripts/` and `render_scripts/`.
  - Use `pyproject.toml` for dependency management.
- **Docker:**
  - `docker-compose.yml` defines services.
  - Use `docker.envrc` for environment-specific configurations.

## Key Files and Directories

- `src/`: Core C++ source files.
- `scripts/`: Python scripts for data processing.
- `resources/`: GIS resources like QGIS styles and shapefiles.
- `output/`: Generated results (e.g., JSON, TXT).
- `include/`: Header files for C++ components.

## Troubleshooting

- **Copying Files from Docker Containers:**
  ```bash
  docker cp <container_id>:/path/to/file ./local/path
  ```

## Notes

- Refer to `README.md` for additional examples and usage details.
- Ensure all new scripts and modules follow the existing directory structure and naming conventions.

---

This document is a living guide. Update it as the project evolves to ensure AI agents remain effective contributors.
