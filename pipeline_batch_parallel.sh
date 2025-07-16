#!/bin/bash

set -e # This will make sure that this bash script will immediately end if any error occurs

cohort=$1

# Define data sources
rbc_m_ratios_data=csvs/cohort_rbc_mem_ratios.csv
hb_correction_data=csvs/cohort_hb_corrections.csv

# Define log file
mkdir -p runs
date=$(date +"%Y_%m_%d_%H_%M_%S")
log_file="runs/${date}_batch.txt"

echo "Received cohort directory: $cohort"
echo "Writing output to log file: $log_file"

# Define batch size for parallel processing
N=5
job_count=0
# Deploy jobs
for patient in "$cohort"/*; do
    patient_id=$(basename "$patient")
    rbc_m_ratio=$(awk -F',' -v name="$patient_id" '$1 == name {print $2}' "$rbc_m_ratios_data")
    hb_correction_value=$(awk -F',' -v name="$patient_id" '$1 == name {print $2}' "$hb_correction_data")
    
    # If the stats file already exists or this item in the source directory is not a PIm directory, skip this patient
    if [[ -f "${patient}/${patient_id}_stats.csv" || ! -d "$patient" || -z "$rbc_m_ratio" || -z "$hb_correction_value" ]]; then
        echo "Skipping ${patient_id}. Either ${patient} is not a PIm directory, or it has already been processed or the Hb correction value or RBC:M ratio were not found in the expected locations."
        echo ${patient_id} >> txt/pipeline_skipped.txt
        continue
    else
        # Deploy background job
        (
            bash pipeline_single.sh "$patient" > "$log_file" 2>&1
            echo ${patient_id} >> txt/pipeline_completed.txt
            echo "PIPELINE COMPLETED: The pipeline has successfully completed for patient ${patient}. ${patient_id} has been recorded in txt/pipeline_completed.txt"
            mkdir -p results
            cp $patient/*_stats.csv results/
        ) &    

        # (()) parentheses are used for evaluating arithmetic expressions
        # [[]] cannot be used for math operations like modulo, addition

        # Throttle (limit number of concurrent jobs to N) to prevent overloading system resources
        ((job_count++))
        if (( job_count % N == 0 )); then
            echo "pipeline_batch_parallel.sh: Waiting for $N jobs to complete before deploying more jobs..."
            wait
        fi
    fi
done

echo "pipeline_batch_parallel.sh: Waiting for remaining jobs to complete..."
wait
echo "pipeline_batch_parallel.sh: All jobs have been completed."

