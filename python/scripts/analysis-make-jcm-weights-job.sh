#!/bin/bash
# Source common functions
source "bbww/scripts/common.sh"


INPUT_DIR="${DEFAULT_DIR}analysis_merge_test_job"
OUTPUT_DIR="${DEFAULT_DIR}analysis_make_jcm_weights_job"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running JCM weights test"
python analysis/make_jcm_weights.py -o $OUTPUT_DIR/testJCM_ROOT   -c passPreSel -r SB --ROOTInputs --i analysis/tests/HistsFromROOTFile.coffea
python analysis/make_jcm_weights.py -o $OUTPUT_DIR/testJCM_Coffea -c passPreSel -r SB -i $INPUT_DIR/test.coffea
python analysis/tests/make_weights_test.py --path $OUTPUT_DIR

