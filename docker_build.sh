#!/usr/bin/env bash

# build the rb-roads image...
DOCKER_BUILDKIT=1 \
    docker \
    build \
    -t rb-roads:latest \
    .
