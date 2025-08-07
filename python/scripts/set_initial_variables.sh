#!/bin/bash

# Default values
do_proxy=false
output="output/"

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --do_proxy) do_proxy=true ;;
        --output) output="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

echo "############### Setting up environment"
if [ "$do_proxy" = true ]; then
    echo "############### Including proxy"
    if [ ! -f "${PWD}/proxy/x509_proxy" ]; then
        echo "Error: x509_proxy file not found!"
        echo "Run manually:"
        echo "mkdir -p proxy && voms-proxy-init -voms cms -valid 192:00 -out ./proxy/x509_proxy"
        echo "and try again."
        exit 1
    fi
    export X509_USER_PROXY=${PWD}/proxy/x509_proxy
    echo "############### Checking proxy"
    voms-proxy-info
fi

return_to_base=false

echo "############### Checking and creating base output directory"
DEFAULT_DIR=${output}
echo "The base output directory is: $DEFAULT_DIR"

echo "############### Checking datasets"
if [[ $(hostname) = *fnal* ]]; then
    DATASETS=metadata/datasets_HH4b_v1p1.yml
else
    DATASETS=metadata/datasets_HH4b_cernbox.yml
fi
echo "The datasets file is: $DATASETS"
