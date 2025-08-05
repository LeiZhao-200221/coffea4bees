#!/bin/bash
# Source common functions
source "bbww/scripts/common.sh"


echo "############### Running trigger emulator test"
python -m unittest base_class.tests.test_trigger_emulator
cd ../

