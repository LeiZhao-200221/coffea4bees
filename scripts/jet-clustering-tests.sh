#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


echo "############### Running jet clustering test"
python coffea4bees/jet_clustering/tests/test_clustering.py 

