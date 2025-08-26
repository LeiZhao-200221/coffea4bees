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
OUTPUT_DIR="$OUTPUT_BASE_DIR/memory_test"
create_output_directory "$OUTPUT_DIR"

display_section_header "Input Datasets"
DATASETS="python/metadata/datasets_HH4b_v1p2.yml"
echo "Using datasets file: $DATASETS"

python src/scripts/memory/memory_test.py \
    --threshold 2200 \
    -o $OUTPUT_DIR/mprofile_ci_test \
    --script runner.py \
        -o test.coffea -t \
        -d GluGluToHHTo4B_cHHH1 \
        -p python/analysis/processors/processor_HH4b.py \
        -y UL18 \
        -op ${OUTPUT_DIR} \
        -m $DATASETS \
        -c python/analysis/metadata/HH4b_signals.yml
