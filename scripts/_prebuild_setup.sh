#!/usr/bin/env bash

if [[ ! -v "$RB_SRC" ]]; then
    export RB_SRC="$(pwd)"
fi
export RBPATH=$RB_SRC
export XDG_DATA_DIRS="${RB_SRC}/share:$XDG_DATA_DIRS"

if [[ ! -v "$RB_DATA" ]]; then
    export RB_DATA="${HOME}/Documents/rb_data"
fi

echo -e "\nSetup rb-road-network environment:"
echo -e "\tRB_SRC=$RB_SRC"
echo -e "\tRB_DATA=$RB_DATA"
echo -e "\n========================\n"

export2envrc() {
    echo -e "export RB_SRC=${RB_SRC}\nexport RB_DATA=${RB_DATA}" | tee ./.envrc
}


if [[ ! -z ./envrc ]]; then
    echo -e "./.envrc doesn't exist! exporting build environment..."
    export2envrc
fi
