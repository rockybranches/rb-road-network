# coding: utf-8

import shapefile as shp
import sys

if __name__=='__main__':
    fpath = "tl_2016_us_county"
    if len(sys.argv) > 1:
        fpath = sys.argv[-1]
    sf = shp.Reader(fpath)
    print("fields:", sf.fields)

    if 'county' in fpath:
        names = [rec['NAME'] for rec in sf.records()]
        print(names)
        print(len(names))
        print("number of counties in shp file:", len(names))
        print("...of approximately 3242 total US counties.")
    elif 'roads' in fpath:
        
