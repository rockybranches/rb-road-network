#!/usr/bin/env sh

# scripts/convert-compose2nix.sh
# convert docker-compose.yml to docker-compose.nix

set -e

nix run github:aksiksi/compose2nix -- \
    -project=rb-road-network \
    -include_env_files=true \
    -env_files='.envrc' \
    -output 'oci-container.nix'
