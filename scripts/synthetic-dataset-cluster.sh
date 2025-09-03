#!/bin/bash
# Source common functions
source "src/scripts/common.sh"

# Setup proxy if needed
setup_proxy

display_section_header "Input Datasets"
# DATASETS=${DATASET:-"coffea4bees/metadata/datasets_HH4b_v1p1.yml"}
DATASETS="coffea4bees/metadata/datasets_HH4b_v1p1.yml"
echo "Using datasets file: $DATASETS"

OUTPUT_DIR="${1:-"output"}/synthetic_dataset_cluster"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Running test processor"
python runner.py -t -o test_synthetic_datasets.coffea -d data  -p coffea4bees/analysis/processors/processor_cluster_4b.py -y UL17 UL18 UL16_preVFP UL16_postVFP  -op $OUTPUT_DIR -m $DATASETS -c coffea4bees/analysis/metadata/cluster_4b.yml
# python runner.py -t -o test_cluster_synthetic_data.coffea -d synthetic_data  -p coffea4bees/analysis/processors/processor_cluster_4b.py -y UL17 UL18 UL16_preVFP UL16_postVFP  -op $OUTPUT_DIR -m $DATASETS -c coffea4bees/analysis/metadata/cluster_4b.yml
# python runner.py -t -o test_synthetic_datasets_Run3.coffea -d data  -p coffea4bees/analysis/processors/processor_cluster_4b.py -y 2022_EE 2022_preEE 2023_BPix 2023_preBPix  -op $OUTPUT_DIR -m coffea4bees/metadata/datasets_HH4b_Run3_fourTag_v3.yml -c coffea4bees/analysis/metadata/cluster_4b_noTTSubtraction.yml

# python runner.py -t -o test_cluster_synthetic_data.coffea -d synthetic_data  -p coffea4bees/analysis/processors/processor_cluster_4b.py -y UL17 UL18 UL16_preVFP UL16_postVFP  -op $OUTPUT_DIR -m $DATASETS -c coffea4bees/analysis/metadata/cluster_4b.yml


# time python runner.py  -o cluster_data_Run2.coffea -d data  -p coffea4bees/analysis/processors/processor_cluster_4b.py -y UL17 UL18 UL16_preVFP UL16_postVFP  -op $OUTPUT_DIR -m $DATASETS -c coffea4bees/analysis/metadata/cluster_4b_noTTSubtraction.yml
# time python runner.py  -o cluster_data_Run2_noTT.coffea -d data  -p coffea4bees/analysis/processors/processor_cluster_4b.py -y UL17 UL18 UL16_preVFP UL16_postVFP  -op $OUTPUT_DIR -m $DATASETS -c coffea4bees/analysis/metadata/cluster_4b.yml
# time python runner.py  -o cluster_synthetic_data_Run2.coffea -d synthetic_data  -p coffea4bees/analysis/processors/processor_cluster_4b.py -y UL17 UL18 UL16_preVFP UL16_postVFP  -op $OUTPUT_DIR -m $DATASETS -c coffea4bees/analysis/metadata/cluster_4b_noTTSubtraction.yml
# python runner.py -t -o test_synthetic_datasets_upto6j.coffea -d data  -p coffea4bees/analysis/processors/processor_cluster_4b.py -y UL18  -op $OUTPUT_DIR -m $DATASETS -c coffea4bees/analysis/metadata/cluster_and_decluster.yml
# python runner.py  -o test_synthetic_datasets_cluster_2023_preBPix.coffea -d data  -p coffea4bees/analysis/processors/processor_cluster_4b.py -y 2023_preBPix   -op hists/ -m coffea4bees/metadata/datasets_HH4b_Run3_fourTag.yml -c coffea4bees/analysis/metadata/cluster_4b_noTTSubtraction.yml

# python  jet_clustering/make_jet_splitting_PDFs.py $OUTPUT_DIR/test_synthetic_datasets_4j_and_5j.coffea  --out jet_clustering/jet-splitting-PDFs-00-02-00 

ls


