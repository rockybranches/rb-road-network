#!/bin/bash
: ${1?"
Usage: $(basename $0) [ outfn (${RB_SRC}/output/justpopResult.txt) ] [lat] [lon] [tons_per_person (4.50)] [stride (0.009)]"}
outfn=${1:-${RB_SRC}/output/justpopResult.txt}
lat=$2
lon=$3
tons_per_person=${4:-4.50}
stride=${5:-0.009}
echo -e "Computing ${outfn}... \n\n\tlat=$lat lon=$lon ...\n\ttons_per_person=$tons_per_person \n\t(stride=$stride)"
$RB_SRC/justPop.exe -f ${outfn} -t $tons_per_person --lat=$lat --lon=$lon --radius=75000 --stride=$stride --nthreads=8 --zoom=0.5
