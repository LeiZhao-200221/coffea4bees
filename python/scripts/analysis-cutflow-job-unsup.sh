#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"


INPUT_DIR="${DEFAULT_DIR}analysis_test_job_unsup"
OUTPUT_DIR="${DEFAULT_DIR}analysis_cutflow_job_unsup"

echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running cutflow test"
python analysis/tests/cutflow_test.py   --inputFile $INPUT_DIR/test_unsup.coffea --knownCounts analysis/tests/known_Counts_unsup.yml

echo "############### Running dump cutflow test"
python analysis/tests/dumpCutFlow.py --input $INPUT_DIR/test_unsup.coffea -o $OUTPUT_DIR/test_dump_cutflow_unsup.yml
ls $OUTPUT_DIR/test_dump_cutflow_unsup.yml


