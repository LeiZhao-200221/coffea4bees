#!/bin/bash
# Source common functions
source "src/scripts/common.sh"

# Setup proxy if needed
setup_proxy

OUTPUT_DIR="${1:-"output"}/sub_sample_dataset_make_dataset_all"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running test processor"
time python runner.py -s -p python/skimmer/processor/sub_sample_MC.py -c python/skimmer/metadata/sub_sampling_MC.yml -y UL17 UL18 UL16_preVFP UL16_postVFP  -d TTToHadronic TTToSemiLeptonic TTTo2L2Nu -op ${OUTPUT_DIR} -o picoaod_datasets_TT_pseudodata_Run2.yml -m python/metadata/datasets_HH4b.yml
ls -R ${OUTPUT_DIR}

