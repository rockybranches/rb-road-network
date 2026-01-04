#!/usr/bin/env bash

set -e

source ./.envrc

python -m venv ${RB_SRC}/venv

source ./venv/bin/activate

pip install -r ${RB_SRC}/requirements.txt

echo -e "...did the setup for the virtualenv at './venv'"
