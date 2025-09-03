#!/bin/bash
# Source common functions
source "src/scripts/common.sh"

# Setup proxy if needed
setup_proxy

OUTPUT_DIR="${1:-"output"}/analysis_test_job_unsup"
echo "############### Checking and creating output directory"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir -p $OUTPUT_DIR
fi

echo "############### Modifying config"
sed -e "s/condor_cores.*/condor_cores: 6/" -e "s/condor_memory.*/condor_memory: 8GB/" coffea4bees/analysis/metadata/unsup4b.yml > $OUTPUT_DIR/unsup4b.yml

cat $OUTPUT_DIR/unsup4b.yml

echo "############### Running test processor"
python runner.py -t -o test_unsup.coffea -d mixeddata data_3b_for_mixed TTToHadronic TTToSemiLeptonic TTTo2L2Nu -p coffea4bees/analysis/processors/processor_unsup.py -y UL17 UL18 UL16_preVFP UL16_postVFP -op $OUTPUT_DIR -m $OUTPUT_DIR/unsup4b.yml -c $OUTPUT_DIR/unsup4b.yml
ls $OUTPUT_DIR

