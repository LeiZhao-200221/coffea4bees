#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"


INPUT_DIR="${DEFAULT_DIR}analysis_test_job"
OUTPUT_DIR="${DEFAULT_DIR}analysis_cutflow_dilepttbar_job"

echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running dump cutflow test"
python analysis/tests/dumpCutFlow.py --input $INPUT_DIR/test_databkgs.coffea -o $OUTPUT_DIR/test_dump_cutflow.yml -c passDilepTtbar


echo "############### Running cutflow test"
python analysis/tests/cutflow_test.py   --inputFile $INPUT_DIR/test_databkgs.coffea --knownCounts analysis/tests/known_Counts_dilepTT.yml

ls $OUTPUT_DIR/test_dump_cutflow.yml

