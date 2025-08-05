#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"


INPUT_DIR="${DEFAULT_DIR}SvB_friendtree_analysis_job"
OUTPUT_DIR="${DEFAULT_DIR}SvB_friendtree_cutflow_job"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running dump cutflow test"
python analysis/tests/dumpCutFlow.py --input $INPUT_DIR/test_SvB_friend.coffea -o $OUTPUT_DIR/test_dump_cutflow_SvB_friend.yml
echo "############### Running cutflow test"
python analysis/tests/cutflow_test.py   --inputFile $INPUT_DIR/test_SvB_friend.coffea --knownCounts analysis/tests/known_Counts_SvB_friendtree.yml
ls $OUTPUT_DIR/test_dump_cutflow_SvB_friend.yml

