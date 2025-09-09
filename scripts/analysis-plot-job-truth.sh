#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


OUTPUT_DIR="${1:-"output"}/analysis_plot_job_truth"
display_section_header "Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

display_section_header "Running test processor"
python  coffea4bees/plots/makePlotsTruthStudy.py coffea4bees/analysis/hists/testTruth.coffea -m coffea4bees/plots/metadata/plotsSignal.yml --out ${OUTPUT_DIR}
display_section_header "Checking if pdf files exist"
ls ${OUTPUT_DIR}/RunII/pass4GenBJets00/fourTag/SR/otherGenJet00_pt.pdf

