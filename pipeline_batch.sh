#!/bin/bash

set -e # This will make sure that this bash script will immediately end if any error occurs

cohort=$1
# cohort="{$1%/}" # Source directory containing patient directories, with the trailing slash removed
rbc_m_ratios_data=csvs/cohort_rbc_mem_ratios.csv
hb_correction_data=csvs/cohort_hb_corrections.csv

# Define log file
mkdir -p runs
date=$(date +"%Y_%m_%d_%H_%M_%S")
log_file="runs/${date}_batch.txt"

echo "Received cohort directory: $cohort"
echo "Writing output to log file: $log_file"

for patient in "$cohort"/*; do
    patient_id=$(basename "$patient")
    
    # If the stats file already exists or this item in the source directory is not a PIm directory, skip this patient
    if [[ -f "${patient}/${patient_id}_stats.csv" || ! -d "$patient" ]]; then
        echo "Skipping: ${patient_id} (already processed or not a directory)"
        continue
    else
        # Ensure the RBC:M ratio and Hb correction values are available for this patient
        rbc_m_ratio=$(awk -F',' -v name="$patient_id" '$1 == name {print $2}' "$rbc_m_ratios_data")
        if [[ -z "$rbc_m_ratio" ]]; then
            echo "ERROR: RBC:Membrane ratio not found for patient ${patient_id} in ${rbc_m_ratios_data}. Marking as skipped."
            echo ${patient_id} >> txt/pipeline_skipped.txt
            continue
            # exit 1
        else
            echo "Recieved rbc:membrane ratio of ${rbc_m_ratio} for patient ${patient_id}"
        fi

        hb_correction_value=$(awk -F',' -v name="$patient_id" '$1 == name {print $2}' "$hb_correction_data")
        if [[ -z "$hb_correction_value" ]]; then
            echo "ERROR: Hb correction value not found for patient ${patient_id} in ${hb_correction_data}. Marking as skipped."
            echo ${patient_id} >> txt/pipeline_skipped.txt
            continue
            # exit 1
        else
            echo "Recieved Hb correction value of ${hb_correction_value} for patient ${patient_id}"
        fi

        bash pipeline_single.sh "$patient" > "$log_file" 2>&1
        echo ${patient_id} >> txt/pipeline_completed.txt
        echo "PIPELINE COMPLETED: The pipeline has successfully completed for patient ${dir_basename} and the patient has been added to txt/pipeline_completed.txt"

        # Copy the regional measurements over to the results directory
        # This way if the original .csv file is deleted, the latest computed regional measurements are still available
        mkdir -p results
        cp $patient/*_stats.csv results/ 
    fi
done
