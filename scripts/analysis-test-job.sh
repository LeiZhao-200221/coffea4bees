#!/bin/bash
# Source common functions
source "src/scripts/common.sh"

# Parse output base argument
OUTPUT_BASE_DIR=$(parse_output_base_arg "output/" "$@")
if [ $? -ne 0 ]; then
    echo "Error parsing output base argument. Use --output-base DIR to specify the output directory."
    exit 1
fi

# Create output directory
create_output_directory "$OUTPUT_BASE_DIR/analysis_test_job"

# Modify the config file
display_section_header "Modifying config"
sed -e "s|hist_cuts: .*|hist_cuts: [ passPreSel, passSvB, failSvB ]|" coffea4bees/analysis/metadata/HH4b.yml > $OUTPUT_BASE_DIR/analysis_test_job/HH4b.yml
cat $OUTPUT_BASE_DIR/analysis_test_job/HH4b.yml

# Call the main analysis_test.sh script with Run3-specific parameters
bash coffea4bees/scripts/run_analysis_processor.sh \
    --output-base "$OUTPUT_BASE_DIR" \
    --datasets "data TTToHadronic TTToSemiLeptonic TTTo2L2Nu" \
    --year "UL17 UL18 UL16_preVFP UL16_postVFP" \
    --output-filename "test_databkgs.coffea" \
    --output-subdir "analysis_test_job" \
    --config $OUTPUT_BASE_DIR/analysis_test_job/HH4b.yml \
    # --additional-flags "--debug"
