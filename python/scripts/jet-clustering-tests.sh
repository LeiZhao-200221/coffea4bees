#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"


echo "############### Running jet clustering test"
python jet_clustering/tests/test_clustering.py 

