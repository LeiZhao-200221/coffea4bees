#!/bin/bash
# Source common functions
source "src/scripts/common.sh"

# Setup proxy if needed
setup_proxy

display_section_header "Input Datasets"
DATASETS=${DATASET:-"coffea4bees/metadata/datasets_HH4b_v1p1.yml"}
echo "Using datasets file: $DATASETS"

INPUT_DIR="${1:-"output"}/SvB_friendtree"
OUTPUT_DIR="${1:-"output"}/SvB_friendtree_analysis_job"
display_section_header "Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

display_section_header "Modifying config"
if [[ $(hostname) = *fnal* ]]; then
    sed -e "s|# SvB: \"metadata.*|SvB: \/srv\/$INPUT_DIR\/make_friend_SvB.json@@SvB|" -e "s|# SvB_MA: \"metadata.*|SvB_MA: \/srv\/$INPUT_DIR\/make_friend_SvB.json@@SvB_MA|" -e "s|SvB   : 'analysis/.*||"  -e "s|SvB_MA: 'analysis/.*||" coffea4bees/analysis/metadata/HH4b_signals.yml > $OUTPUT_DIR/HH4b_signals.yml
else
    sed -e "s|# SvB: \"metadata.*|SvB: /builds/${CI_PROJECT_PATH}/$INPUT_DIR/make_friend_SvB.json@@SvB|" -e "s|# SvB_MA: \"metadata.*|SvB_MA: /builds/${CI_PROJECT_PATH}/$INPUT_DIR/make_friend_SvB.json@@SvB_MA|" -e "s|SvB   : 'analysis/.*||"  -e "s|SvB_MA: 'analysis/.*||"  coffea4bees/analysis/metadata/HH4b_signals.yml > $OUTPUT_DIR/HH4b_signals.yml
fi
cat $OUTPUT_DIR/HH4b_signals.yml

display_section_header "Running test processor"
python runner.py -t -o test_SvB_friend.coffea -d GluGluToHHTo4B_cHHH1 -p coffea4bees/analysis/processors/processor_HH4b.py -y UL18 -op $OUTPUT_DIR -c $OUTPUT_DIR/HH4b_signals.yml -m $DATASETS
ls -lR ${OUTPUT_DIR}

