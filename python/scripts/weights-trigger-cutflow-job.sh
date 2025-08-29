#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


INPUT_DIR="${1:-"output"}/weights_trigger_analysis_job"
OUTPUT_DIR="${1:-"output"}/weights_trigger_cutflow_job"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running dump cutflow test"
python python/analysis/tests/dumpCutFlow.py --input $INPUT_DIR/test_trigWeight.coffea -o $OUTPUT_DIR/test_dump_cutflow_trigWeight.yml
echo "############### Running cutflow test"
python python/analysis/tests/cutflow_test.py   --inputFile $INPUT_DIR/test_trigWeight.coffea --knownCounts python/analysis/tests/known_Counts_trigWeight.yml
ls $OUTPUT_DIR/test_dump_cutflow_trigWeight.yml

