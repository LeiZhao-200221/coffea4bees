#!/bin/bash
# Source common functions
source "src/scripts/common.sh"

# Setup proxy if needed
setup_proxy

INPUT_DIR="${1:-"output"}/synthetic_dataset_make_dataset_Run3"
OUTPUT_DIR="${1:-"output"}/synthetic_dataset_analyze_Run3"
display_section_header "Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

display_section_header "Changing metadata"
if [[ $(hostname) = *fnal* ]]; then
    echo "No change in metadata."
    sed -e "s#output#${1:-"output"}#" coffea4bees/metadata/datasets_synthetic_test_Run3.yml > $OUTPUT_DIR/datasets_synthetic_test_Run3.yml
else
    sed -e "s#\/srv#\/builds\/${CI_PROJECT_PATH}#" coffea4bees/metadata/datasets_synthetic_test_Run3.yml > $OUTPUT_DIR/datasets_synthetic_test_Run3.yml
fi
cat $OUTPUT_DIR/datasets_synthetic_test_Run3.yml

# display_section_header "Modifying dataset file with skimmer ci output"
# cat coffea4bees/metadata/datasets_ci.yml
# python src/utils/merge_yaml_datasets.py -m coffea4bees/metadata/datasets_HH4b.yml -f coffea4bees/skimmer/metadata/picoaod_datasets_declustered_data_test_UL18A.yml  -o coffea4bees/metadata/datasets_synthetic_seed17_test.yml

#/builds/johnda/coffea4bees/coffea4bees/skimmer/GluGluToHHTo4B_cHHH1_UL18/picoAOD_seed5.root
#/builds/johnda/coffea4bees/python
#johnda/coffea4bees
#/builds/coffea4bees/skimmer/GluGluToHHTo4B_cHHH1_UL18/picoAOD_seed5.root


# display_section_header "Changing metadata"
# sed -e "s/apply_FvT.*/apply_FvT: false/" -e "s/apply_trig.*/apply_trigWeight: false/" -e "s/run_SvB.*/run_SvB: false/"  coffea4bees/analysis/metadata/HH4b.yml > $OUTPUT_DIR/tmp.yml
# cat $OUTPUT_DIR/tmp.yml
#display_section_header "Running test processor"
#time python runner.py -o test_synthetic_data_test.coffea -d data -p coffea4bees/analysis/processors/processor_HH4b.py -y UL18  -op $OUTPUT_DIR/ -c $OUTPUT_DIR/HH4b_synthetic_data.yml -m coffea4bees/metadata/datasets_synthetic_seed17.yml


display_section_header "Running test processor "
# python src/utils/merge_yaml_datasets.py -m coffea4bees/metadata/datasets_HH4b.yml -f coffea4bees/skimmer/metadata/picoaod_datasets_declustered_test_UL18.yml  -o coffea4bees/metadata/datasets_synthetic_test.yml
# python src/utils/merge_yaml_datasets.py -m coffea4bees/metadata/datasets_synthetic_seed17.yml -f coffea4bees/skimmer/metadata/picoaod_datasets_declustered_GluGluToHHTo4B_cHHH1_Run2_seed17.yml -o coffea4bees/metadata/datasets_synthetic_seed17.yml
#cat coffea4bees/metadata/datasets_synthetic_test.yml

time python runner.py -o test_synthetic_datasets.coffea -d synthetic_data  -p coffea4bees/analysis/processors/processor_HH4b.py -y 2023_BPix  -op $OUTPUT_DIR/ -c coffea4bees/analysis/metadata/HH4b_synthetic_data.yml -m $OUTPUT_DIR/datasets_synthetic_test_Run3.yml

# time python runner.py -o test_synthetic_datasets.coffea -d data GluGluToHHTo4B_cHHH1 -p coffea4bees/analysis/processors/processor_HH4b.py -y UL18  -op $OUTPUT_DIR/ -c coffea4bees/analysis/metadata/HH4b_synthetic_data.yml -m $OUTPUT_DIR/datasets_synthetic_test.yml
# time python runner.py -o test_synthetic_datasets_Run3.coffea -d data  -p coffea4bees/analysis/processors/processor_HH4b.py -y 2022_EE  -op ${OUTPUT_DIR} -c coffea4bees/analysis/metadata/HH4b_synthetic_data.yml -m coffea4bees/metadata/datasets_HH4b_Run3_fourTag.yml


