#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


INPUT_DIR="${1:-"output"}/synthetic_dataset_cluster"
OUTPUT_DIR="${1:-"output"}/synthetic_dataset_plot_job"
display_section_header "Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi
display_section_header "Running test processor"
python  coffea4bees/jet_clustering/make_jet_splitting_PDFs.py $INPUT_DIR/test_synthetic_datasets.coffea --doTest  --out $OUTPUT_DIR/jet-splitting-PDFs-test
display_section_header "Checking if pdf files exist"
ls $OUTPUT_DIR/jet-splitting-PDFs-test/clustering_pdfs_vs_pT_RunII.yml 
ls $OUTPUT_DIR/jet-splitting-PDFs-test/test_sampling_pt_1b0j_1b0j_mA.pdf 

