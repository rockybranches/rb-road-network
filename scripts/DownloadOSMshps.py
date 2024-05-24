#!/usr/local/bin/python3
import requests, os, zipfile, argparse, sys, shutil, subprocess, shlex, time
from functools import wraps
from collections import OrderedDict
import geopandas as gpd
import pandas as pd

rb_data_path = os.environ["RB_DATA"]
zips_path = os.path.join(rb_data_path, "gis_osm_roads_extra/gis_osm_zips/")
geom_path = os.path.join(rb_data_path, "gis_osm_roads_extra/")
states_csv = os.path.join(rb_data_path, 'state_fips.csv')
backup_path = os.path.join(rb_data_path, ".backup_gis_osm_roads")
final_path = os.path.join(rb_data_path, "gis_osm_roads/")
dl_root = "http://download.geofabrik.de/north-america/us/"

class State(object):
    def __init__(self, name, abbrev, fips, which='roads'):
        self.name = name; self.abbrev = abbrev; self.fips = fips
        self.which = which

    @property
    def sname(self):
        return self.name.lower().replace(" ","-")
    
    @property
    def url(self):
        sname = self.sname
        dl_url = dl_root + f"{sname}-200401-free.shp.zip"
        return dl_url

    @property
    def zpath(self):
        return os.path.join(zips_path, self.url.split("/")[-1])

    @property
    def gpath(self):
        return os.path.join(geom_path, self.sname + "_geom/")

    @property
    def spath(self):
        which = self.which
        return os.path.join(self.gpath, f"gis_osm_{which}_free_1.shp")
    
    @property
    def dpath(self):
        which = self.which
        return os.path.join(self.gpath, f"gis_osm_{which}_free_1.dbf")

class WeirdState(object):
    def __init__(self, name, names, abbrev, fips, which='roads'):
        self.name = name; self.abbrev = abbrev; self.fips = fips
        self.names = names; self.which = which
        self.sub_states = [State(name, abbrev, fips, which=which) for name in names]

    @property
    def url(self):
        snames = self.sname
        dl_urls = [dl_root + self.name.lower() + "/" + f"{sn}-200401-free.shp.zip" for sn in snames]
        return dl_urls

    def __getattr__(self, aname):
        if aname not in self.__dir__():
            return [getattr(sst, aname) for sst in self.sub_states]
        return getattr(self, aname)


class US(object):
                 
    weird_states = {'California': ['NorCal', 'SoCal']}

    def check_weird(f):
        @wraps(f)
        def wrapper(*args, **kwds):
            if all([isinstance(a, list) for a in args[1:]]):
                print("(Weird state)")
                for a in zip(*args[1:]):
                    f(args[0], *a, **kwds)
                return
            f(*args, **kwds)
        return wrapper
                 
    def __init__(self, path=states_csv, which='roads'):
        self.which = which
        self.path = path
        self.states = OrderedDict()
        self._load_states()
        self.gdfs = []
        
    def _load_states(self):
        state_info = []
        with open(self.path, 'r') as pf:
            state_info = pf.readlines()
        for si in state_info[1:]:
            sname, sabbrev, sfips = si.split(",")
            if sname in list(US.weird_states.keys()):
                print("(weird state): ", sname)
                self.states.update({sname: WeirdState(sname, US.weird_states[sname], sabbrev, sfips, which=self.which)})
            else:
                self.states.update({sname: State(sname, sabbrev, sfips, which=self.which)})

    def get_list(self, kind='obj', style=None):
        styles = {
            None: lambda x: str(x),
            'lower': lambda x: str.lower(x),
            'upper': lambda x: str.upper(x),
            'title': lambda x: str.title(x),
            'int': lambda x: int(x),
        }
        if kind == 'obj':
            return list(self.states.values())
        return [styles[style](getattr(st, kind)) for st in self.states.values()]

    def download_all(self, overwrite=False):
        for st in self.states.values():
            print("Attempting download of: \t", st.name, " ", st.url, st.zpath)
            self.download(st.url, st.zpath, overwrite=overwrite)

    @check_weird
    def download(self, sturl, zp, overwrite=False):
        if not overwrite:
            if os.path.exists(zp):
                print('download: (skipped!)... already have: {}'.format(zp))
                return
        r = requests.get(sturl, stream=True)
        with open(zp, "wb") as zff:
            for chunk in r.iter_content(chunk_size=128):
                zff.write(chunk)
        print('download: ...downloaded: {} , to: {}'.format(sturl,zp))

    def unzip_all(self, overwrite=False):
        for st in self.states.values():
            self.unzip(st.zpath, st.gpath, overwrite=overwrite)

    @check_weird
    def unzip(self, zp, gp, overwrite=False):
        if not overwrite:
            if os.path.exists(gp):
                print('(skipped!)... already have: {}'.format(gp))
                return
        print(f"unzip: trying {zp}...")
        with zipfile.ZipFile(zp) as zff:
            zff.extractall(path=gp)
        print(f"unzip: ...extracted {zp} ... to: {gp}")

    def shpcat_all(self, backup=True):
        which = self.which
        ppaths = []
        print(f"shpcat_all: concatenating all *{which}* shp files...")
        if backup:
            print("shpcat_all: first, backing up previous roads file...")
            shutil.copytree(f"{final_path}", backup_path + "_{:d}/".format(int(time.time())))
            print("...done with backup...")
        for ii, st in enumerate(self.states.values()):
            self.shpcat(st.spath, st.dpath)
            if (ii % 5) == 0 and ii > 0:
                gdf = gpd.GeoDataFrame(pd.concat(self.gdfs,sort=True))
                ppaths.append(f"{final_path}/gis_osm_{which}_free_part_{ii}.shp")
                print("chunkfile...", ppaths[-1])
                gdf.to_file(ppaths[-1])
                del self.gdfs[:]
        print("merging chunkfiles...")
        gpd.GeoDataFrame(pd.concat([gpd.read_file(pff) for pff in ppaths],
                                   sort=True)).tofile(f"{final_path}/gis_osm_{which}_free_1.shp")
        return
    
    @check_weird
    def shpcat(self, sp, dp):
        which = self.which
        print("loading...", sp)
        self.gdfs.append(gpd.read_file(sp))
        

if __name__=="__main__":
    us = US()
    parser = argparse.ArgumentParser(
        prog="DownloadOSMshps",
        description="Download, process geofabrik OSM data (shps).")
    parser.add_argument("-dA", "--download-all", help="attempt to download any shp files for all US states.", action="store_true", default=False)
    parser.add_argument("-f", "--force", help="force download files, overwriting any existing data (default is to skip existing files)", action="store_true", default=False)
    parser.add_argument("-uA", "--unzip-all", help="unzip all downloaded ZIP files", action='store_true', default=False)
    parser.add_argument("-d", "--download", help="download shp file(s) corresponding to the state name (e.g. 'California'), specified by the argument(s) following this option.", action="append")
    parser.add_argument("-u", "--unzip", help="unzip the shp file(s) specified by the argument(s) following this option.", action="append")
    parser.add_argument("-c", "--shpcat", help="concatenate all current SHP road files, optionally backup existing concatenated SHP file (default).", action='store_true', default=False)
    parser.add_argument("-w", "--which-features", help="specify which features to use for '--shpcat' (e.g. 'roads', 'transport', 'railways', etc.)", action='append', default=['roads'])
    parser.add_argument("-nb", "--no-backup", help="If specified, *skip* the backup of the previously concatenated SHP file before shpcat (default is to perform the backup).", action='store_false')
    args = parser.parse_args()
    if args.download_all:
        us.download_all(overwrite=args.force)
    if args.unzip_all:
        us.unzip_all(overwrite=args.force)
    if args.download:
        for ff in args.download:
            st = us.states[ff]
            us.download(st.url, st.zpath, overwrite=args.force)
    if args.unzip:
        for ff in args.unzip:
            st = us.states[ff]
            us.unzip(st.zpath, st.gpath, overwrite=args.force)
    if args.shpcat:
        us.which = args.which_features[0]
        us.shpcat_all(backup=args.no_backup)
    print("\nDone.")
