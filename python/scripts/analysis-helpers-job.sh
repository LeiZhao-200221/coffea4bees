#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


echo "############### Running makeweights test"
python python/analysis/tests/topCand_test.py

