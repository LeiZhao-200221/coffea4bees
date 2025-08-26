#!/bin/bash
# Source common functions
source "src/scripts/common.sh"

# Setup proxy if needed
setup_proxy

display_section_header "Input Datasets"
DATASETS=${DATASET:-"python/metadata/datasets_HH4b.yml"}
echo "Using datasets file: $DATASETS"

OUTPUT_DIR="${1:-"output"}/analysis_test_job_truthStudy"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running test processor"
python runner.py -t    -o testTruth.coffea -d GluGluToHHTo4B_cHHH1 -p python/analysis/processors/processor_genmatch_HH4b.py -y UL18  -op $OUTPUT_DIR -m $DATASETS  -c python/analysis/metadata/HH4b_genmatch.yml

