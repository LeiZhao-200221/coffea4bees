#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"


INPUT_DIR="${DEFAULT_DIR}synthetic_dataset_analyze_Run3"
OUTPUT_DIR="${DEFAULT_DIR}synthetic_dataset_analyze_cutflow_Run3"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running dump cutflow test"
python analysis/tests/dumpCutFlow.py --input $INPUT_DIR/test_synthetic_datasets.coffea -o $OUTPUT_DIR/test_dump_cutflow_synthetic_datasets.yml
echo "############### Running cutflow test"
python analysis/tests/cutflow_test.py   --inputFile $INPUT_DIR/test_synthetic_datasets.coffea --knownCounts analysis/tests/known_counts_test_synthetic_datasets_Run3.yml --error_threshold 0.05
ls $OUTPUT_DIR/test_dump_cutflow_synthetic_datasets.yml


