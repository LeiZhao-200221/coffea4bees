#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"

# Setup proxy if needed
setup_proxy

display_section_header "Input Datasets"
DATASETS=${DATASET:-"metadata/datasets_HH4b.yml"}
echo "Using datasets file: $DATASETS"

OUTPUT_DIR="${1:-"output"}/classifier_friendtree_job"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Modifying config"
if [[ $(hostname) = *fnal* ]]; then
    sed -e "s#make_.*#make_classifier_input: \/srv\/$OUTPUT_DIR\/#" analysis/metadata/HH4b_classifier_inputs.yml > $OUTPUT_DIR/HH4b_classifier_inputs.yml
else
    sed -e "s#make_.*#make_classifier_input: /builds/${CI_PROJECT_PATH}/python/$OUTPUT_DIR/#" analysis/metadata/HH4b_classifier_inputs.yml > $OUTPUT_DIR/HH4b_classifier_inputs.yml
fi
cat $OUTPUT_DIR/HH4b_classifier_inputs.yml

echo "############### Running test processor"
python runner.py -t -o classifier_friendtree.yml -d data GluGluToHHTo4B_cHHH1 -p analysis/processors/processor_HH4b.py -y UL18 -op $OUTPUT_DIR -c $OUTPUT_DIR/HH4b_classifier_inputs.yml -m $DATASETS
ls $OUTPUT_DIR

