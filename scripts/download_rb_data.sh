#/usr/bin/env bash


# download rb_data
cd $RB_DATA
gdrive download --recursive 1vNoqU15SJejDt4P5dLtPXmtUZFALexZV
# export state_fips -> csv
gdrive export --mime text/csv 15eFbEiAanDuZb3m6qPecBR7QVSzOnbQWsFIcaq8LE3E
cd -

# download county pop
$RB_SRC/scripts/downloadCountyPop/downloadCountyPop.sh
