#!/bin/bash
# Source common functions
source "src/scripts/common.sh"

# Setup proxy if needed
setup_proxy

display_section_header "Input Datasets"
DATASETS=${DATASET:-"coffea4bees/metadata/datasets_HH4b.yml"}
echo "Using datasets file: $DATASETS"

INPUT_DIR="${1:-"output"}/weights_trigger_friendtree"
OUTPUT_DIR="${1:-"output"}/weights_trigger_analysis_job"
display_section_header "Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

display_section_header "Modifying config"
if [[ $(hostname) = *fnal* ]]; then
    sed -e "s|trigWeight: .*|trigWeight: \/srv\/$INPUT_DIR\/trigger_weights_friends.json@@trigWeight|" coffea4bees/analysis/metadata/HH4b_signals.yml > $OUTPUT_DIR/trigger_weights_HH4b.yml
else
    sed -e "s|trigWeight: .*|trigWeight: /builds/${CI_PROJECT_PATH}/$INPUT_DIR/trigger_weights_friends.json@@trigWeight|" coffea4bees/analysis/metadata/HH4b_signals.yml > $OUTPUT_DIR/trigger_weights_HH4b.yml
fi
cat $OUTPUT_DIR/trigger_weights_HH4b.yml

display_section_header "Running test processor"
python runner.py -t -o test_trigWeight.coffea -d GluGluToHHTo4B_cHHH1 -p coffea4bees/analysis/processors/processor_HH4b.py -y UL18 -op $OUTPUT_DIR -c $OUTPUT_DIR/trigger_weights_HH4b.yml -m $DATASETS
ls -lR ${OUTPUT_DIR}

