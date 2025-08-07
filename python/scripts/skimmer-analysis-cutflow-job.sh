#!/bin/bash
# Source common functions
source "bbww/scripts/common.sh"


INPUT_DIR="${DEFAULT_DIR}skimmer_analysis_test_job"
OUTPUT_DIR="${DEFAULT_DIR}skimmer_analysis_cutflow_job"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running dump cutflow test"
python analysis/tests/dumpCutFlow.py --input $INPUT_DIR/test_skimmer.coffea -o $OUTPUT_DIR/test_dump_skimmer_cutflow.yml
echo "############### Running cutflow test"
python analysis/tests/cutflow_test.py   --inputFile $INPUT_DIR/test_skimmer.coffea --knownCounts analysis/tests/known_Counts_skimmer.yml
ls $OUTPUT_DIR/test_dump_skimmer_cutflow.yml

