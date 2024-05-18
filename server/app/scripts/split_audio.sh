#!/bin/bash
echo "Running split_audio.py with file_name=$1"
python ./scripts/split_audio.py --file_name="$1"