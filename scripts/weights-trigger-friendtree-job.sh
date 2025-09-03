#!/bin/bash
# Source common functions
source "src/scripts/common.sh"

# Setup proxy if needed
setup_proxy

display_section_header "Input Datasets"
DATASETS=${DATASET:-"coffea4bees/metadata/datasets_HH4b.yml"}
echo "Using datasets file: $DATASETS"

OUTPUT_DIR="${1:-"output"}/weights_trigger_friendtree_job"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Modifying config"
if [[ $(hostname) = *fnal* ]]; then
    sed -e "s#make_.*#make_classifier_input: \/srv\/$OUTPUT_DIR\/#" coffea4bees/analysis/metadata/trigger_weights.yml > $OUTPUT_DIR/trigger_weights.yml
else
    sed -e "s#make_.*#make_classifier_input: /builds/${CI_PROJECT_PATH}/$OUTPUT_DIR/#" coffea4bees/analysis/metadata/trigger_weights.yml > $OUTPUT_DIR/trigger_weights.yml
fi
cat $OUTPUT_DIR/trigger_weights.yml

echo "############### Running test processor"
python runner.py -t -o trigger_weights_friends.json -d GluGluToHHTo4B_cHHH1 -p coffea4bees/analysis/processors/processor_trigger_weights.py -y UL18 -op $OUTPUT_DIR  -c $OUTPUT_DIR/trigger_weights.yml -m $DATASETS
ls $OUTPUT_DIR

