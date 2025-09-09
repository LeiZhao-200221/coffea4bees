#!/bin/bash
# Source common functions
source "src/scripts/common.sh"

# Parse output base argument
OUTPUT_BASE_DIR=$(parse_output_base_arg "output" "$@")
if [ $? -ne 0 ]; then
    echo "Error parsing output base argument. Use --output-base DIR to specify the output directory. Default DIR=output/"
    exit 1
fi

# Create output directory
JOB="tools_merge_test"
INPUT_DIR=$OUTPUT_BASE_DIR/analysis_merge_test
OUTPUT_DIR=$OUTPUT_BASE_DIR/$JOB
create_output_directory "$OUTPUT_DIR"

display_section_header "Running JCM weights test"
run_command python coffea4bees/analysis/jcm_tools/make_jcm_weights.py \
    -o $OUTPUT_DIR/testJCM_ROOT   \
    -c passPreSel -r SB --ROOTInputs \
    --i coffea4bees/analysis/tests/HistsFromROOTFile.coffea

run_command python coffea4bees/analysis/jcm_tools/make_jcm_weights.py \
    -o $OUTPUT_DIR/testJCM_Coffea \
    -c passPreSel -r SB \
    -i $INPUT_DIR/test.coffea

run_command python coffea4bees/analysis/tests/make_weights_test.py \
    --path $OUTPUT_DIR

