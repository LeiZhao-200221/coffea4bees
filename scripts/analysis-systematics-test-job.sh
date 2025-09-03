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
OUTPUT=$OUTPUT_BASE_DIR/analysis_systematics_test_job
create_output_directory "$OUTPUT"

display_section_header "Modifying HH4b_signals.yml"
sed -e "s|condor_memory: 2GB|chunksize: 10000|g" \
    coffea4bees/analysis/metadata/HH4b_signals.yml > $OUTPUT/HH4b_signals_modified.yml


# Call the main run_analysis_processor.sh script
bash coffea4bees/scripts/run_analysis_processor.sh \
    --output-base "$OUTPUT_BASE_DIR" \
    --dataset-metadata "coffea4bees/metadata/datasets_HH4b_v1p2.yml" \
    --datasets "GluGluToHHTo4B_cHHH1" \
    --year "UL18" \
    --output-filename "test_systematics.coffea" \
    --output-subdir "analysis_systematics_test_job" \
    --config $OUTPUT/HH4b_signals_modified.yml \
    --additional-flags "--systematics others"
    # --additional-flags "--debug"
