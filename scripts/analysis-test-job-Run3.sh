#!/bin/bash
# Source common functions
source "src/scripts/common.sh"

# Setup proxy if needed
setup_proxy

display_section_header "Input Datasets"
DATASETS=${DATASET_RUN3:-"coffea4bees/metadata/datasets_synthetic_test_Run3.yml"}
echo "Using datasets file: $DATASETS"

# Create output directory
OUTPUT_DIR="${1:-"output"}/analysis_test_job_Run3"
create_output_directory $OUTPUT_DIR

echo "############### Running test processor"
python runner.py -t -o test.coffea -d data  -p coffea4bees/analysis/processors/processor_HH4b.py -y 2022_EE 2022_preEE 2023_BPix 2023_preBPix -op $OUTPUT_DIR -m $DATASETS -c coffea4bees/analysis/metadata/HH4b_run_fastTopReco.yml



ls $OUTPUT_DIR


