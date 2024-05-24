#!/usr/bin/env bash
export RB_SRC=$RB_SRC && \
    export RBPATH=$RB_SRC && \
    export XDG_DATA_DIRS="${RB_SRC}/share:$XDG_DATA_DIRS" && \
    export RB_DATA=$RB_DATA
