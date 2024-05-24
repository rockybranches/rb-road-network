#!/bin/bash
$RB_SRC/justPop.exe -f ${1:-./output/DickensHancockResult.txt} --lat=33.246889 --lon=-82.915661 --radius=75000 --stride=0.009 --nthreads=8 --zoom=0.5
