#!/usr/bin/python3
import shapefile as shp
import sys,os

if __name__=='__main__':
    dpath = os.environ["RB_DATA"]
    fpath = "tl_2016_us_county"
    fpath = "/".join([fpath,]*2)
    if len(sys.argv) > 1:
        fpath = sys.argv[-1]
        fpath = os.path.join(fpath,list(filter(lambda ff: os.path.splitext(ff)[-1]==".shp",
                                               os.listdir(os.path.join(dpath, fpath))))[0])
    print("fpath=",fpath)
    sf = shp.Reader(os.path.join(dpath, fpath))
    print("fields:", sf.fields)

    if 'county' in fpath:
        names = [rec['NAME'] for rec in sf.records()]
        print("some county names: ", names[0:10], "...")
        print(len(names))
        print("number of counties in shp file:", len(names))
        print("...of approximately 3242 total US counties.")
    elif 'roads' in fpath:
        pass
