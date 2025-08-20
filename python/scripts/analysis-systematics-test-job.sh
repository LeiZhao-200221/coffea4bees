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
create_output_directory "$OUTPUT_BASE_DIR/analysis_systematics_test_job"

# Call the main run_analysis_processor.sh script
bash python/scripts/run_analysis_processor.sh \
    --output-base "$OUTPUT_BASE_DIR" \
    --datasets "GluGluToHHTo4B_cHHH1" \
    --year "UL18" \
    --output-filename "test_systematics.coffea" \
    --output-subdir "analysis_systematics_test_job" \
    --config python/analysis/metadata/HH4b_signals.yml \
    --additional-flags "--systematics others"
    # --additional-flags "--debug"
