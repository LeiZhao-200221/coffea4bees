#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"


INPUT_DIR="${1:-"output"}/analysis_merge_test_job"

echo "############### Running iPlot test"
python plots/tests/iPlot_test.py --inputFile $INPUT_DIR/test.coffea

