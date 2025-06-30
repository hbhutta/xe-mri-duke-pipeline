#!/bin/bash

: '
Author: Haad Bhutta
Updated: June 30, 2025

Description:
This script runs the separate files that make up the pipeline. The order of the 
files that are run cannot be changed. 

The input to this pipeline is the path toa cohort directory containing individual patient directories.

Example usage:
bash pipeline_batch.sh cohort/
'

set -e # This will make sure that this bash script will immediately end if any error occurs

cohort=$1

for patient in "$cohort"/*; do
    if [ -d "$patient" ]; then
        echo "Processing patient directory: $patient"
        bash pipeline_single.sh "$patient"
    else
        echo "Skipping non-directory: $patient"
    fi
done