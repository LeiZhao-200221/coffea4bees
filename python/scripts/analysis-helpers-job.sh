#!/bin/bash
# Source common functions
source "bbww/scripts/common.sh"


echo "############### Running makeweights test"
python analysis/tests/topCand_test.py

