#!/bin/bash
# Source common functions
source "base_class/scripts/common.sh"

# Setup proxy if needed
setup_proxy --do_proxy

OUTPUT_DIR="${1:-"output"}/synthetic_dataset_make_dataset_all_2025"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running test processor"

#new_seed=0

# Run2
#sed -e "s/declustering_rand_seed: [0-9]/declustering_rand_seed: $new_seed/" skimmer/metadata/declustering.yml > ${OUTPUT_DIR}/declustering_seed_${new_seed}.yml
#cat ${OUTPUT_DIR}/declustering_seed_${new_seed}.yml
#time python runner.py -s -p skimmer/processor/make_declustered_data_4b.py -c ${OUTPUT_DIR}/declustering_seed_${new_seed}.yml -y UL17 UL18 UL16_preVFP UL16_postVFP -d data -op ${OUTPUT_DIR}/ -o picoaod_datasets_declustered_data_Run2_seed${new_seed}.yml -m metadata/datasets_HH4b.yml --condor   # --dask

# Run3
#sed -e "s/declustering_rand_seed:.*/declustering_rand_seed: $new_seed/" skimmer/metadata/declustering_noTT_subtraction.yml > ${OUTPUT_DIR}/declustering_noTT_subtraction_seed_${new_seed}.yml
#cat ${OUTPUT_DIR}/declustering_noTT_subtraction_seed_${new_seed}.yml
#time python runner.py -s -p skimmer/processor/make_declustered_data_4b.py -c ${OUTPUT_DIR}/declustering_noTT_subtraction_seed_${new_seed}.yml -y 2022_EE 2022_preEE 2023_BPix 2023_preBPix -d data -op ${OUTPUT_DIR}/ -o picoaod_datasets_declustered_data_Run3_v9_seed${new_seed}.yml -m metadata/datasets_HH4b_Run3_fourTag_v3.yml --condor   # --dask


for new_seed in {1..1}
do
  echo ${new_seed}
  sed -e "s/declustering_rand_seed:.*/declustering_rand_seed: $new_seed/" skimmer/metadata/declustering_noTT_subtraction.yml > ${OUTPUT_DIR}/declustering_noTT_subtraction_seed_${new_seed}.yml
  cat ${OUTPUT_DIR}/declustering_noTT_subtraction_seed_${new_seed}.yml
  #time python runner.py -s -p skimmer/processor/make_declustered_data_4b.py -c ${OUTPUT_DIR}/declustering_noTT_subtraction_seed_${new_seed}.yml -y 2022_EE 2022_preEE 2023_BPix 2023_preBPix -d data -op ${OUTPUT_DIR}/ -o picoaod_datasets_declustered_data_Run3_v10_seed${new_seed}.yml -m metadata/datasets_HH4b_Run3_fourTag_2025_skims.yml --condor   # --dask
  time python runner.py -s -p skimmer/processor/make_declustered_data_4b.py -c ${OUTPUT_DIR}/declustering_noTT_subtraction_seed_${new_seed}.yml -y 2023_preBPix -d data -op ${OUTPUT_DIR}/ -o picoaod_datasets_declustered_data_Run3_v10_seed${new_seed}.yml -m metadata/datasets_HH4b_Run3_fourTag_2025_skims.yml --condor   # --dask
done


# time python runner.py -s -p skimmer/processor/make_declustered_data_4b.py -c skimmer/metadata/declustering_signal.yml -y UL17 UL18 UL16_preVFP UL16_postVFP -d GluGluToHHTo4B_cHHH1 -op ${OUTPUT_DIR}/ -o picoaod_datasets_declustered_GluGluToHHTo4B_cHHH1_Run2_seed17.yml -m metadata/datasets_HH4b.yml

#ls -R skimmer/


