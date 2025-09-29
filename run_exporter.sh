#!/bin/bash

# Activate virtual environment and run the Kadena exporter
source venv/bin/activate
python3 kadena_exporter.py "$@"