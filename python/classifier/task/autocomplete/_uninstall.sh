#!/bin/bash
python -m python.classifier.task.autocomplete._bind exit
pkill -9 -u $USER -xf "python -m python.classifier.task.autocomplete._core"
complete -r "./pyml.py"