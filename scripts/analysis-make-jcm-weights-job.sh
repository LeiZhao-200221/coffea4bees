#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


INPUT_DIR="${1:-"output"}/analysis_merge_test_job"
OUTPUT_DIR="${1:-"output"}/analysis_make_jcm_weights_job"
display_section_header "Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

display_section_header "Running JCM weights test"
python coffea4bees/analysis/jcm_tools/make_jcm_weights.py -o $OUTPUT_DIR/testJCM_ROOT   -c passPreSel -r SB --ROOTInputs --i coffea4bees/analysis/tests/HistsFromROOTFile.coffea
python coffea4bees/analysis/jcm_tools/make_jcm_weights.py -o $OUTPUT_DIR/testJCM_Coffea -c passPreSel -r SB -i $INPUT_DIR/test.coffea
python coffea4bees/analysis/tests/make_weights_test.py --path $OUTPUT_DIR

