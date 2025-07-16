#!/bin/bash

set -e # This will make sure that this bash script will immediately end if any error occurs

cohort=$1 # Source directory containing patient directories

for patient in "$cohort"/*; do
    if [ -d "$patient" ]; then
        bash clean_single.sh "$patient" 
    else
        echo "Skipping non-directory: $patient"
    fi
done
