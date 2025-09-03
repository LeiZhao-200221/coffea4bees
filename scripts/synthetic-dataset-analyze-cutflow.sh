#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


INPUT_DIR="${1:-"output"}/synthetic_dataset_analyze"
OUTPUT_DIR="${1:-"output"}/synthetic_dataset_analyze_cutflow"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running dump cutflow test"
python coffea4bees/analysis/tests/dumpCutFlow.py --input $INPUT_DIR/test_synthetic_datasets.coffea -o $OUTPUT_DIR/test_dump_cutflow_synthetic_datasets.yml
echo "############### Running cutflow test"
python coffea4bees/analysis/tests/cutflow_test.py   --inputFile $INPUT_DIR/test_synthetic_datasets.coffea --knownCounts coffea4bees/analysis/tests/known_counts_test_synthetic_datasets.yml
ls $OUTPUT_DIR/test_dump_cutflow_synthetic_datasets.yml

