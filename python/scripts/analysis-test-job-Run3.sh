#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"

# Setup proxy if needed
setup_proxy

display_section_header "Input Datasets"
DATASETS=${DATASET_RUN3:-"metadata/datasets_HH4b_Run3_cernbox.yml"}
echo "Using datasets file: $DATASETS"

# Create output directory
OUTPUT_DIR="${1:-"output"}/analysis_test_job_Run3"
create_output_directory $OUTPUT_DIR

echo "############### Running test processor"
python runner.py -t -o test.coffea -d data  -p analysis/processors/processor_HH4b.py -y 2022_EE 2022_preEE 2023_BPix 2023_preBPix -op $OUTPUT_DIR -m $DATASETS -c analysis/metadata/HH4b_run_fastTopReco.yml



ls $OUTPUT_DIR


