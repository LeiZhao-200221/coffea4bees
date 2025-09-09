#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


INPUT_DIR="${1:-"output"}/analysis_test_unsup"
OUTPUT_DIR="${1:-"output"}/analysis_plot_job_unsup"
display_section_header "Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

display_section_header "Running test processor"
python coffea4bees/plots/makePlots_unsup.py $INPUT_DIR/test_unsup.coffea --doTest   -o $OUTPUT_DIR/ -m coffea4bees/plots/metadata/plotsAll_unsup.yml 
display_section_header "Checking if pdf files exist"
ls $OUTPUT_DIR/RunII/passPreSel/fourTag/SR/mix_v0/v4j_mass.pdf
ls $OUTPUT_DIR/RunII/passPreSel/fourTag/SR_vs_SB/mix_v0/v4j_mass.pdf
ls $OUTPUT_DIR/RunII/passPreSel/fourTag/SR/mix_v0/quadJet_selected_lead_vs_subl_m.pdf 
ls $OUTPUT_DIR/RunII/passPreSel/threeTag/SR/data_3b_for_mixed/quadJet_selected_lead_vs_subl_m.pdf 

