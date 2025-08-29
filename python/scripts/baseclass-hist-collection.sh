#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


echo "############### Running hist collection test"
python -m src.tests.hist_collection
