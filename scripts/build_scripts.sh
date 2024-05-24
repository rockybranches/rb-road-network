#!/bin/bash

# build all scripts

export includes="-I${RB_SRC}/include -I/usr/include"
export cflags="-Wall -g -std=gnu++17 $(pkg-config --cflags gtk+-3.0)"
export output_dir="${RB_SRC}/scripts/bin/"
export libs=" "

echo "includes = ${includes}"

# get sourcefiles (.c, .cc, .cpp)
for ff in $(ls -ltr $RB_SRC/scripts/ | grep '^d' | awk '{print $9}'); do
    
    # !! ************* compile only for folders with 'deps.txt' *************
    if [ -f "${RB_SRC}/scripts/${ff}/deps.txt" ]; then
	echo -e "\n"
	export local_cflags="${cflags} "$(echo $(ls "${RB_SRC}/scripts/${ff}" | grep -E ".*\.(cc$|c$|cpp$)"))" "
	export local_libs="${libs} "$(cat "${RB_SRC}/scripts/${ff}/deps.txt")" "
	echo "local_libs : ${local_libs} "
	echo "local_cflags : ${local_cflags} "
	cd ${RB_SRC}/scripts/${ff}
	( g++ ${local_cflags} ${includes} -o ${output_dir}/${ff}.exe ${local_libs} -lpthread -lstdc++fs &&
	    echo -e "\n${ff} done.\n") || echo -e "\n${ff} failed.\n"
    fi
done

echo -e "\nDone. List of compiled scripts:"
ls -lt $RB_SRC/scripts/bin/
