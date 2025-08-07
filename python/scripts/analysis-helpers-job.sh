#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"


echo "############### Running makeweights test"
python analysis/tests/topCand_test.py

