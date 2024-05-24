#!/usr/bin/env bash

# download county population data from google drive
echo -e "\nstarting script to download county population data from google drive...\n"

# output path
outpath=${RB_DATA}/county_pop/

# list of file IDs to check from Google Drive (Southeast)
files2check=$(cat $RB_SRC/scripts/downloadCountyPop/fids.txt)

mkdir -p $outpath
cd $outpath
# Southeast
for DOCID in $(cat $RB_SRC/scripts/downloadCountyPop/fids.txt);
do
    gdrive export $DOCID
done

function ExportFromParent() {
    for fgpth in $(gdrive list --query " '$1' in parents" | awk '{ print($1) }' | tail -c +4);
    do
	gdrive export $fgpth --mime text/csv
    done
}

parent_dirs=$(gdrive list --query " '10DhnJjQGckEfvUGGGMGIesG8bFPuQs6g' in parents" | awk '$3=="dir" {print $(1)}')
for fdir in $parent_dirs;
do
    ExportFromParent $fdir
done

cd -

echo -e "\n............\n\n...done downloading updated county population data to:\n\t$outpath."
