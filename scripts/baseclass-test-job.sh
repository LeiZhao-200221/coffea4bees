#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


INPUT_DIR="${1:-"output"}/analysis_merge_test_job"
OUTPUT_DIR="${1:-"output"}/baseclass_test_job"
display_section_header "Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi
display_section_header "Running base class test"
python src/tests/dumpPlotCounts.py --input $INPUT_DIR/test.coffea --output $OUTPUT_DIR/test_dumpPlotCounts.yml
python src/tests/plots_test.py --inputFile $INPUT_DIR/test.coffea --known src/tests/known_PlotCounts.yml
ls $OUTPUT_DIR/test_dumpPlotCounts.yml

