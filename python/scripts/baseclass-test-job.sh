#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"


INPUT_DIR="${1:-"output"}/analysis_merge_test_job"
OUTPUT_DIR="${1:-"output"}/baseclass_test_job"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi
echo "############### Running base class test"
python base_class/tests/dumpPlotCounts.py --input $INPUT_DIR/test.coffea --output $OUTPUT_DIR/test_dumpPlotCounts.yml
python base_class/tests/plots_test.py --inputFile $INPUT_DIR/test.coffea --known base_class/tests/known_PlotCounts.yml
ls $OUTPUT_DIR/test_dumpPlotCounts.yml

