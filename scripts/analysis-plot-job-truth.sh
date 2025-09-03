#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


OUTPUT_DIR="${1:-"output"}/analysis_plot_job_truth"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running test processor"
python  coffea4bees/plots/makePlotsTruthStudy.py coffea4bees/analysis/hists/testTruth.coffea -m coffea4bees/plots/metadata/plotsSignal.yml --out ${OUTPUT_DIR}
echo "############### Checking if pdf files exist"
ls ${OUTPUT_DIR}/RunII/pass4GenBJets00/fourTag/SR/otherGenJet00_pt.pdf

