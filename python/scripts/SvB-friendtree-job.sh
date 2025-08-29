#!/bin/bash
# Source common functions
source "src/scripts/common.sh"

# Setup proxy if needed
setup_proxy

display_section_header "Input Datasets"
DATASETS=${DATASET:-"python/metadata/datasets_HH4b_v1p1.yml"}
echo "Using datasets file: $DATASETS"

OUTPUT_DIR="${1:-"output"}/SvB_friendtree_job"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Modifying config"
if [[ $(hostname) = *fnal* ]]; then
    sed -e "s#/srv/output/tmp/#\/srv\/$OUTPUT_DIR\/#" python/analysis/metadata/HH4b_make_friend_SvB.yml > $OUTPUT_DIR/HH4b_make_friend_SvB.yml
else
    sed -e "s#/srv/output/tmp/#/builds/${CI_PROJECT_PATH}/$OUTPUT_DIR/#" python/analysis/metadata/HH4b_make_friend_SvB.yml > $OUTPUT_DIR/HH4b_make_friend_SvB.yml
fi
cat $OUTPUT_DIR/HH4b_make_friend_SvB.yml

echo "############### Running test processor"
python runner.py -t -o make_friend_SvB.coffea -d GluGluToHHTo4B_cHHH1 -p python/analysis/processors/processor_HH4b.py -y UL18 -op $OUTPUT_DIR -c $OUTPUT_DIR/HH4b_make_friend_SvB.yml -m $DATASETS
ls $OUTPUT_DIR

