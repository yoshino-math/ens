#!/bin/sh
PYTHON=python3
ENS_PATH="$(cd "$(dirname "$0")" && pwd)/"
PYTHONPATH="${ENS_PATH}src" $PYTHON -m ens.chain "$@"
