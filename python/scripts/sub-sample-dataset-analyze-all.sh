#!/bin/bash
# Source common functions
source "src/scripts/common.sh"

# Setup proxy if needed
setup_proxy

OUTPUT_DIR="${1:-"output"}/sub_sample_dataset_analyze_all"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

# echo "############### Changing metadata"
# sed -e "s/apply_FvT.*/apply_FvT: false/" -e "s/apply_trig.*/apply_trigWeight: false/" -e "s/run_SvB.*/run_SvB: false/"  python/analysis/metadata/HH4b.yml > ${OUTPUT_DIR}/tmp.yml
# cat ${OUTPUT_DIR}/tmp.yml
#echo "############### Running test processor"
#time python runner.py -o test_synthetic_data_test.coffea -d data -p python/analysis/processors/processor_HH4b.py -y UL18  -op ${OUTPUT_DIR} -c python/analysis/metadata/HH4b_synthetic_data.yml -m python/metadata/datasets_synthetic_seed17.yml


echo "############### Running test processor "
# python python/metadata/merge_yaml_datasets.py -m python/metadata/datasets_HH4b.yml -f ${OUTPUT_DIR}/picoaod_datasets_TT_pseudodata_Run2.yml  -o ${OUTPUT_DIR}datasets_TT_pseudodata_Run2.yml
#cat ${OUTPUT_DIR}/datasets_synthetic_test.yml
time python runner.py -o TT_pseudodata_datasets.coffea -d ps_data_TTToSemiLeptonic ps_data_TTTo2L2Nu ps_data_TTToHadronic -p python/analysis/processors/processor_HH4b.py -y UL18 UL17 UL16_preVFP UL16_postVFP  -op ${OUTPUT_DIR} -c python/analysis/metadata/HH4b_rerun_SvB.yml -m python/metadata/datasets_TT_pseudodata_Run2.yml
#time python runner.py -o histAll_TT.coffea            -d TTToHadronic TTToSemiLeptonic TTTo2L2Nu                         -p python/analysis/processors/processor_HH4b.py  -y UL17 UL18 UL16_preVFP UL16_postVFP  -op analysis/hists/ -c python/analysis/metadata/HH4b_rerun_SvB.yml 

