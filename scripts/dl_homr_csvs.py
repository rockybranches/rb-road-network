#!/usr/bin/python
import requests
import os

if __name__=="__main__":
    base_url="https://www.ncei.noaa.gov/data/global-historical-climatology-network-daily/access/"
    with open("/media/Data/US_CLIMATE/HOMR/www.ncei.noaa.gov/data/global-historical-climatology-network-daily/access/index.html","r") as htmlf:
        flist = htmlf.readlines()
    flist = [fl for fl in flist if "href=" in fl and "csv" in fl]
    flist = [fl.split("href=")[1].split('">')[0].strip('"') for fl in flist] 
    for fl in flist:
        fpath = "/media/Data/US_CLIMATE/HOMR/{}".format(fl)
        if not os.path.isfile(fpath):
            print(fl)
            response = requests.get(base_url + fl) 
            response.encoding = 'utf-8'
            if response.status_code==200:
                with open(fpath,"w") as fout: 
                    fout.write(response.text)

    
    
