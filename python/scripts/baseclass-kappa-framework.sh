#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


echo "############### Running kappa framework test"
python -m src.tests.kappa_framework
