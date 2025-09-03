#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


echo "############### Running makeweights test"
python coffea4bees/analysis/tests/topCand_test.py

