#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"

# Setup proxy if needed
setup_proxy

display_section_header "Input Datasets"
DATASETS=${DATASET:-"metadata/datasets_HH4b.yml"}
echo "Using datasets file: $DATASETS"

INPUT_DIR="${1:-"output"}/SvB_friendtree_job"
OUTPUT_DIR="${1:-"output"}/SvB_friendtree_analysis_job"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Modifying config"
if [[ $(hostname) = *fnal* ]]; then
    sed -e "s|SvB: .*|SvB: \/srv\/$INPUT_DIR\/make_friend_SvB.json@@SvB|" -e "s|SvB_MA: .*|SvB_MA: \/srv\/$INPUT_DIR\/make_friend_SvB.json@@SvB_MA|" analysis/metadata/HH4b_signals.yml > $OUTPUT_DIR/HH4b_signals.yml
else
    sed -e "s|SvB: .*|SvB: /builds/${CI_PROJECT_PATH}/python/$INPUT_DIR/make_friend_SvB.json@@SvB|" -e "s|SvB_MA: .*|SvB_MA: /builds/${CI_PROJECT_PATH}/python/$INPUT_DIR/make_friend_SvB.json@@SvB_MA|" analysis/metadata/HH4b_signals.yml > $OUTPUT_DIR/HH4b_signals.yml
fi
cat $OUTPUT_DIR/HH4b_signals.yml

echo "############### Running test processor"
python runner.py -t -o test_SvB_friend.coffea -d GluGluToHHTo4B_cHHH1 -p analysis/processors/processor_HH4b.py -y UL18 -op $OUTPUT_DIR -c $OUTPUT_DIR/HH4b_signals.yml -m $DATASETS
ls -lR ${OUTPUT_DIR}

