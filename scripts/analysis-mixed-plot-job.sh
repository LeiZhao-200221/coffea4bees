#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


OUTPUT_DIR="${1:-"output"}/analysis_mixed_plot_job/"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running test processor"
python python/plots/makePlotsMixed.py python/analysis/hists/testMixedBkg_master.coffea python/analysis/hists/testMixedData_master.coffea --combine_input_files -m python/plots/metadata/plotsMixed.yml   -o ${OUTPUT_DIR}
echo "############### Checking if pdf files exist"
ls ${OUTPUT_DIR}/RunII/passPreSel/fourTag/SR/

#python python/plots/makePlots.py python/analysis/hists/test.coffea    -o ${OUTPUT_DIR} -m python/plots/metadata/plotsAll.yml
#ls ${OUTPUT_DIR}/RunII/passPreSel/fourTag/SR/SvB_MA_ps_zh.pdf
#ls ${OUTPUT_DIR}/RunII/passPreSel/fourTag/SR/SvB_MA_ps_hh.pdf
#ls ${OUTPUT_DIR}/RunII/passPreSel/fourTag/SR_vs_SB/data/SvB_MA_ps.pdf
#ls ${OUTPUT_DIR}/RunII/passPreSel/fourTag/SR_vs_SB/HH4b/SvB_MA_ps.pdf
#ls ${OUTPUT_DIR}/RunII/passPreSel_vs_failSvB_vs_passSvB/fourTag/SR/data/v4j_mass.pdf
#ls ${OUTPUT_DIR}/RunII/passPreSel_vs_failSvB_vs_passSvB/fourTag/SR/HH4b/v4j_mass.pdf 
#ls ${OUTPUT_DIR}/RunII/passPreSel/fourTag/SR/data/quadJet_min_dr_close_vs_other_m.pdf 
#ls ${OUTPUT_DIR}/RunII/passPreSel/fourTag/SR/HH4b/quadJet_min_dr_close_vs_other_m.pdf
#ls ${OUTPUT_DIR}/RunII/passPreSel/threeTag/SR/Multijet/quadJet_min_dr_close_vs_other_m.pdf 

