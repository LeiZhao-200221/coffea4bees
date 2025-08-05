#!/bin/bash
# Source common functions
source "bbww/scripts/common.sh"


echo "############### Running kappa framework test"
python -m base_class.tests.kappa_framework
