#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


INPUT_DIR="${1:-"output"}/analysis_test_job_unsup"
OUTPUT_DIR="${1:-"output"}/analysis_cutflow_job_unsup"

echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running dump cutflow test"
python coffea4bees/analysis/tests/dumpCutFlow.py --input $INPUT_DIR/test_unsup.coffea -o $OUTPUT_DIR/test_dump_cutflow_unsup.yml
ls $OUTPUT_DIR/test_dump_cutflow_unsup.yml

echo "############### Running cutflow test"
python coffea4bees/analysis/tests/cutflow_test.py   --inputFile $INPUT_DIR/test_unsup.coffea --knownCounts coffea4bees/analysis/tests/known_Counts_unsup.yml
