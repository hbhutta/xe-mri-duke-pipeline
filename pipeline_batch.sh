#!/bin/bash

set -e # This will make sure that this bash script will immediately end if any error occurs

cohort=$1 # Source directory containing patient directories
rbc_m_ratios_data=csvs/cohort_rbc_mem_ratios.csv
hb_correction_data=csvs/cohort_hb_corrections.csv

# Define log file
timestamp=$(date +"%Y_%m_%d_%H%M%S")
log_file="runs/${timestamp}_batch.txt"

echo "Received cohort directory: $cohort"
echo "Writing output to log file: $log_file"

for patient in "$cohort"/*; do
    if [ -d "$patient" ]; then
        patient_id=$(basename "$patient")

        rbc_m_ratio=$(awk -F',' -v name="$patient" '$1 == name {print $2}' "$rbc_m_ratios_data") 
        if [[ -z "$rbc_m_ratio" ]]; then
            echo "ERROR: RBC:Membrane ratio not found for patient ${patient_id} in ${rbc_m_ratios_data}. Exiting."
            exit 1
        else
            echo "Recieved rbc:membrane ratio of ${rbc_m_ratio} for patient ${patient_id}"
        fi

        hb_correction_value=$(awk -F',' -v name="$patient" '$1 == name {print $2}' "$hb_correction_data")
        if [[ -z "$hb_correction_value" ]]; then
            echo "ERROR: Hb correction value not found for patient ${patient_id} in ${hb_corrections_data}. Exiting."
            exit 1
        else
            echo "Recieved Hb correction value of ${hb_correction_value} for patient ${patient_id}"
        fi

        bash pipeline_single.sh "$patient" > "$log_file" 2>&1
    else
        echo "Skipping non-directory: $patient"
    fi
done
