#!/bin/bash
echo "Running conversion.py with folder_name=$1 model_name=$2"
python ./scripts/conversion.py --folder_name="$1" --model_name="$2"