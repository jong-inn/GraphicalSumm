#!/bin/bash
echo "Running summarize.py with folder_name=$1 model_name=$2"
python ./scripts/summarize.py --folder_name="$1" --model_name="$2"