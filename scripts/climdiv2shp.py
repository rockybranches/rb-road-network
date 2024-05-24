#!/usr/bin/python
import shapefile as shp
import os
import us

elcodes = {
    "01": "PRCP",
    "02": "TAVE",
    "27": "TMAX",
    "28": "TMIN"
}

# Dictionary : [ statecodes -> (state names, fips) ]
stns = [st.name for st in us.states.STATES if "District" not in st.name]
stcodes= dict( ( "{:02d}".format(ii+1), dict([("STNAME",sn),("STFIPS",us.states.lookup(sn).fips)]) ) for ii, sn in enumerate(sorted(stns)) )


if __name__=="__main__":
    pdict = {}

    fns = ["climdiv-pcpncy-v1.0.0-20190904", "climdiv-tmaxcy-v1.0.0-20190904",
           "climdiv-tmincy-v1.0.0-20190904",] # "climdiv-tmpccy-v1.0.0-20190904"

    for current_fn in fns:
        with open(os.path.join("../data/climate_data/", current_fn)) as pcpf:
            for pline in pcpf:
                pcountycode = stcodes[pline[0:2]]["STFIPS"] + pline[2:5] # reformat countycode -> ( State_FIPS + COUNTY_FIPS )
                pyear = pline[7:11]
                pvals = pline[11:95].split()
                if int(pyear) > 1990 and all(float(pv) > -80.0 for pv in pvals):
                    if pcountycode not in list(pdict.keys()):
                        pdict[pcountycode] = {}
                    pelname = elcodes[pline[5:7]]
                    if pelname not in list(pdict[pcountycode].keys()):
                        pdict[pcountycode][pelname] = {}
                        pdict[pcountycode][pelname]["V"] = [0]*12 # []
                        pdict[pcountycode][pelname]["YEARS"] = [pyear,]
                    else:
                        pdict[pcountycode][pelname]["YEARS"].append(pyear)
                        # pdict[pcountycode][pelname]["V"].append([float(pv) for pv in pvals])
                        pdict[pcountycode][pelname]["V"] = [float(pv)+float(pd) for pv, pd in zip(pvals, list(pdict[pcountycode][pelname]["V"]))]
            
    for pcode in list(pdict.keys()):
        for pel in list(pdict[pcode].keys()):
            pdict[pcode][pel]["V"] = [pd / len(pdict[pcode][pel]["YEARS"]) for pd in list(pdict[pcode][pel]["V"])]

    
    import datetime
    months = ["{:02d}".format(i)+datetime.date(2008, i, 1).strftime('%B').upper()[0:3] for i in range(1, 13)]
    print(months)

    for pcode in list(pdict.keys()):
        for pel in list(pdict[pcode].keys()):
            for mi, month in enumerate(months):
                pdict[pcode][pel][month] = pdict[pcode][pel]["V"][mi]


    import json
    with open("../data/climate_data/climate.json","w") as jf:
        json.dump(pdict, jf)
                
    # # write fields
    # sfw = shp.Writer("../data/tl_2016_us_county/tl_2016_us_county")
    # for pel in list(elcodes.values()):
    #     for mo in months:
    #         sfw.field(pel+mo, 'N', decimal=3)
    # sfw.close()
    
    # # read all records
    # sfr = shp.Reader("../data/tl_2016_us_county/tl_2016_us_county")
    # records = sfr.records()
    # rfields = sfr.fields
    # print("Fields: ", rfields)
    # sfr.close()
    # print()
    
    # # write modified records
    # for ir, rec in enumerate(records):
    #     pcode = rec['STATEFP']+rec['COUNTYFP']
    #     print("IR",ir,"PCODE:" , pcode)
    #     for pel in list(pdict[pcode].keys()):
    #         pvals = pdict[pcode][pel]['V']
    #         for iv, pv in pvals:
    #             print(pel+months[iv], pv)
    #             rec[pel+months[iv]] = pv
    #     sfw = shp.Writer("../data/tl_2016_us_county/tl_2016_us_county")
    #     for ii in range(0,ir):
    #         sfw.null()
    #     sfw.record(**rec.as_dict())
    #     sfw.close()
            
