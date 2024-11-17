#!/usr/bin/env python3

import os
import sys

rb_src = os.path.abspath(os.path.dirname(__file__))


def exec_full_download_script():
    os.popen(os.path.join(rb_src, "scripts", "download-gis-osm-roads.sh"))

        
def main(states=None):
    if states is None:
        exec_full_download_script()
        sys.exit(0)
    else:
        template_fpath = os.path.join(rb_src, "resources", "gis_osm_roads_SINGLE_update.aria2")
        with open(template_fpath, 'r') as f:
            aria_f.read()

if __name__ == '__main__':
    main()
