#!/usr/bin/env bash

source ./.envrc

python -m venv ${RB_SRC}/venv

source ./venv/bin/activate

pip install -r ${RB_SRC}/requirements.txt
