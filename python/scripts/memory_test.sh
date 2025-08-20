#!/bin/bash
# Source common functions
source "src/scripts/common.sh"

# Setup proxy if needed
setup_proxy

display_section_header "Input Datasets"
DATASETS=${DATASET:-"python/metadata/datasets_HH4b.yml"}
echo "Using datasets file: $DATASETS"

OUTPUT_DIR="${1:-"output"}/memory_test"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running memory test"
sed -e "s#  workers: 4.*#  workers: 1\n  maxchunks: 1#" python/analysis/metadata/HH4b_signals.yml > $OUTPUT_DIR/HH4b_memory_test.yml
python src/tests/memory_test.py --threshold 3600 -o $OUTPUT_DIR/mprofile_ci_test --script runner.py -o test.coffea -d GluGluToHHTo4B_cHHH1 -p python/analysis/processors/processor_HH4b.py -y UL18 -op ${OUTPUT_DIR} -m $DATASETS -c $OUTPUT_DIR/HH4b_memory_test.yml
ls $OUTPUT_DIR/mprofile_ci_test.png

