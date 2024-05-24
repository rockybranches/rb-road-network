#/usr/bin/env bash
sudo docker run -it \
     --mount type=bind,source="${RB_DATA}",target=/rb_data \
     --mount type=bind,source="$(realpath ${RB_DATA}/logs)",target=/rb_data/logs \
     --mount type=bind,source="$(realpath ${RB_SRC}/output)",target=/rb_app/output \
     rb-roads:latest 
