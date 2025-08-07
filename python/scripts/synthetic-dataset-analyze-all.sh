#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"

# Setup proxy if needed
setup_proxy

OUTPUT_DIR="${1:-"output"}/synthetic_dataset_analyze_all"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running test processor"

#time python runner.py -o synthetic_data_RunII_seedXXX.coffea -d synthetic_data data -p analysis/processors/processor_HH4b.py -y UL17 UL18 UL16_preVFP UL16_postVFP -op ${OUTPUT_DIR} -c analysis/metadata/HH4b_run_fastTopReco.yml -m metadata/datasets_HH4b_fourTag.yml
#time python runner.py -o synthetic_data_only_RunII_seedXXX.coffea -d synthetic_data  -p analysis/processors/processor_HH4b.py -y UL17 UL18 UL16_preVFP UL16_postVFP -op ${OUTPUT_DIR} -c analysis/metadata/HH4b_run_fastTopReco.yml -m metadata/datasets_HH4b_fourTag.yml
#time python runner.py -o test_synthetic_data_seedXXX_hTRW.coffea -d synthetic_data  -p analysis/processors/processor_HH4b.py -y UL17 UL18 UL16_preVFP UL16_postVFP -op ${OUTPUT_DIR} -c analysis/metadata/HH4b_run_fastTopReco.yml -m metadata/datasets_HH4b_fourTag.yml

#time python runner.py -o synthetic_data_Run3_v8_new_16seeds.coffea -d synthetic_data data -p analysis/processors/processor_HH4b.py -y 2022_preEE 2022_EE 2023_preBPix 2023_BPix  -op ${OUTPUT_DIR} -c analysis/metadata/HH4b_run_fastTopReco.yml -m metadata/datasets_HH4b_Run3_fourTag_v8.yml --condor

time python runner.py -o synthetic_data_Run3_2025_v2.coffea -d synthetic_data data -p analysis/processors/processor_HH4b.py -y 2022_preEE 2022_EE 2023_preBPix 2023_BPix  -op ${OUTPUT_DIR} -c analysis/metadata/HH4b_run_fastTopReco.yml -m metadata/datasets_HH4b_Run3_fourTag_2025_skims.yml --condor


#time python runner.py -o synthetic_data_closure_Run2_seed0.coffea  -d synthetic_data TTToHadronic TTToSemiLeptonic TTTo2L2Nu data  -p analysis/processors/processor_HH4b.py  -y UL17 UL18 UL16_preVFP UL16_postVFP  -op ${OUTPUT_DIR} -c analysis/metadata/HH4b_synthetic_closure.yml -m metadata/datasets_HH4b.yml

# time python runner.py -o histAll_bkg.coffea            -d TTToHadronic TTToSemiLeptonic TTTo2L2Nu data                         -p analysis/processors/processor_HH4b.py  -y UL17 UL18 UL16_preVFP UL16_postVFP  -op ${OUTPUT_DIR} -c analysis/metadata/HH4b_run_fastTopReco.yml
#time python runner.py -o histAll_bkg.coffea            -d TTToHadronic TTToSemiLeptonic TTTo2L2Nu data                         -p analysis/processors/processor_HH4b.py  -y UL17 UL18 UL16_preVFP UL16_postVFP  -op ${OUTPUT_DIR} -c analysis/metadata/HH4b_run_slowTopReco.yml


#time python runner.py -o test_synthetic_data_seedXXX_noPSData.coffea -d synthetic_data  -p analysis/processors/processor_HH4b.py -y UL17 UL18 UL16_preVFP UL16_postVFP -op ${OUTPUT_DIR} -c analysis/metadata/HH4b_run_fastTopReco.yml -m metadata/datasets_HH4b_fourTag.yml
#time python runner.py -o nominal_noTT.coffea -d data -p analysis/processors/processor_HH4b.py -y UL17 UL18 UL16_preVFP UL16_postVFP -op ${OUTPUT_DIR} -c analysis/metadata/HH4b_subtract_tt.yml 



## echo "############### Running test processor HHSignal"
## 
## time python runner.py -o test_synthetic_GluGluToHHTo4B_cHHH1.coffea -d GluGluToHHTo4B_cHHH1 -p analysis/processors/processor_HH4b.py -y UL17 UL18 UL16_preVFP UL16_postVFP -op ${OUTPUT_DIR} -c analysis/metadata/HH4b_synthetic_data.yml -m metadata/datasets_synthetic_seed17.yml
## 
## time python runner.py -o nominal_GluGluToHHTo4B_cHHH1.coffea -d GluGluToHHTo4B_cHHH1 -p analysis/processors/processor_HH4b.py -y UL17 UL18 UL16_preVFP UL16_postVFP -op ${OUTPUT_DIR} -c analysis/metadata/HH4b.yml


