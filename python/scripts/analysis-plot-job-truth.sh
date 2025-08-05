#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"


OUTPUT_DIR="${1:-"output"}/analysis_plot_job_truth"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running test processor"
python  plots/makePlotsTruthStudy.py analysis/hists/testTruth.coffea -m plots/metadata/plotsSignal.yml --out ${OUTPUT_DIR}
echo "############### Checking if pdf files exist"
ls ${OUTPUT_DIR}/RunII/pass4GenBJets00/fourTag/SR/otherGenJet00_pt.pdf

