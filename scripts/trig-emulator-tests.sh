#!/bin/bash
# Source common functions
source "src/scripts/common.sh"


echo "############### Running trigger emulator test"
python -m unittest coffea4bees.analysis.tests.test_trigger_emulator
cd ../

