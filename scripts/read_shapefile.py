#!/usr/bin/env python3
import sys
from pathlib import Path
import geopandas as gpd

rb_data_dirpath = os.environ["RB_DATA"]


def main(filename: str = "tl_2016_us_county.shp", data_dirpath: str = rb_data_dirpath):
    fpath = Path(data_dirpath).joinpath(filename)
    print("Reading from ", fpath)
    gdf = gpd.read_file(str(fpath.parent))
    print(gdf.head())


if __name__ == "__main__":
    main()
