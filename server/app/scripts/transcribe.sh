#!/bin/bash
echo "Running transcribe.py with file_name=$1 prompt=$2"
python ./scripts/transcribe.py --file_name="$1" --prompt="$2"