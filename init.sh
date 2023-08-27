#!/bin/bash
cd /Users/tuethomsen/projects/load-electricity-data-from-api/
source .venv/bin/activate
export $(grep -v '^#' .env | xargs)
python electricity_api_loader/main.py
