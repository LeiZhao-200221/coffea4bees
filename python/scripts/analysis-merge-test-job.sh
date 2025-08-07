#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"


OUTPUT_DIR="${1:-"output"}/analysis_merge_test_job"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Merging coffea files"
python analysis/tools/merge_coffea_files.py -f ${1:-"output"}/analysis_test_job/test_databkgs.coffea ${1:-"output"}/analysis_signals_test_job/test_signal.coffea  -o $OUTPUT_DIR/test.coffea

ls $OUTPUT_DIR


