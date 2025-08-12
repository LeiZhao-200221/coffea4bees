#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"

# Setup proxy if needed
setup_proxy

display_section_header "Input Datasets"
DATASETS=${DATASET_RUN3:-"metadata/datasets_synthetic_test_Run3.yml"}
echo "Using datasets file: $DATASETS"

echo "############### Checking and creating output/skimmer directory"
OUTPUT_DIR="${1:-"output"}/synthetic_dataset_make_dataset_Run3"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Changing metadata"
echo "############### Overwritting datasets"
if [[ $(hostname) = *fnal* ]]; then
    sed -e "s#base_path.*#base_path: \/srv\/${OUTPUT_DIR}\/#" -e "s/\#max.*/maxchunks: 1/" -e "s/\#test.*/test_files: 1/" -e "s/\workers:.*/workers: 1/" -e "s/chunksize:.*/chunksize: 1000/"  skimmer/metadata/declustering_noTT_subtraction.yml > $OUTPUT_DIR/declustering_for_test.yml
else
    sed -e "s#base_.*#base_path: \/builds\/${CI_PROJECT_PATH}\/python\/${OUTPUT_DIR}\/#" -e "s/\#max.*/maxchunks: 1/" -e "s/\#test.*/test_files: 1/" -e "s/\workers:.*/workers: 1/" -e "s/chunksize:.*/chunksize: 1000/" -e "s/T3_US_FNALLPC/T3_CH_PSI/" skimmer/metadata/declustering_noTT_subtraction.yml > $OUTPUT_DIR/declustering_for_test.yml
fi
cat $OUTPUT_DIR/declustering_for_test.yml

echo "############### Running test processor"
time python runner.py -s -p skimmer/processor/make_declustered_data_4b.py -c $OUTPUT_DIR/declustering_for_test.yml -y 2023_BPix  -d data  -op $OUTPUT_DIR -o picoaod_datasets_declustered_test_2023_BPix.yml -m $DATASETS

# time python runner.py -s -p skimmer/processor/make_declustered_data_4b.py -c $OUTPUT_DIR/declustering_for_test.yml -y UL18  -d GluGluToHHTo4B_cHHH1 -op $OUTPUT_DIR -o picoaod_datasets_declustered_GluGluToHHTo4B_cHHH1_test_UL18.yml -m metadata/datasets_HH4b.yml
ls -R $OUTPUT_DIR


