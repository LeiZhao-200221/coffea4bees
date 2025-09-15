#!/bin/bash
python -m coffea4bees.classifier.task.autocomplete._bind exit
pkill -9 -u $USER -xf "python -m coffea4bees.classifier.task.autocomplete._core"
complete -r "./pyml.py"