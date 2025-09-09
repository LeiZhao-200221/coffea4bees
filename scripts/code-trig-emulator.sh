#!/bin/bash

display_section_header "Running trigger emulator test"
python -m unittest coffea4bees.analysis.tests.test_trigger_emulator

