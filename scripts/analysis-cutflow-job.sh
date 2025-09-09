#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


INPUT_DIR="${1:-"output"}/analysis_merge_test_job"
OUTPUT_DIR="${1:-"output"}/analysis_cutflow_job"

display_section_header "Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

display_section_header "Running dump cutflow test"
python coffea4bees/analysis/tests/dumpCutFlow.py --input $INPUT_DIR/test.coffea -o $OUTPUT_DIR/test_dump_cutflow.yml


display_section_header "Running cutflow test"
python coffea4bees/analysis/tests/cutflow_test.py   --inputFile $INPUT_DIR/test.coffea --knownCounts coffea4bees/analysis/tests/known_Counts.yml

ls $OUTPUT_DIR/test_dump_cutflow.yml

