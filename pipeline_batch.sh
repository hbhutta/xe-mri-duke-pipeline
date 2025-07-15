#!/bin/bash

:'
Author: Haad Bhutta
Updated: July 15, 2025

Description:
This script runs the separate files that make up the pipeline. The order of the 
files that are run cannot be changed. 

The input to this pipeline is the path toa cohort directory containing individual patient directories.

Example usage:
bash pipeline_batch.sh cohort/
'

set -e # This will make sure that this bash script will immediately end if any error occurs

cohort=$1 # Source directory containing patient directories
rbc_m_ratios_data=csvs/cohort_rbc_mem_ratios.csv

for patient in "$cohort"/*; do
    if [ -d "$patient" ]; then
        echo "Processing patient directory: $patient"
        
        rbc_m_ratio=$(awk -F',' -v name="$patient" '$1 == name {print $2}' "$csv_file")
        if [[ -z "$rbc_m_ratio" ]]; then
            echo "ERROR: RBC:Membrane ratio not found for patient ${patient} in ${rbc_m_ratios_data}. Exiting."
            exit 1
        else
            echo "Recieved rbc:membrane ratio of ${rbc_m_ratio} for patient ${patient}"
        fi

        bash pipeline_single.sh "$patient"
    else
        echo "Skipping non-directory: $patient"
    fi
done
