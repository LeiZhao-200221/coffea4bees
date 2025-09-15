#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


echo "############### Running jet clustering test"
python python/jet_clustering/tests/test_clustering.py 

