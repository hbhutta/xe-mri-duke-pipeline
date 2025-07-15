#!/bin/bash

: '
Author: Haad Bhutta
Updated: June 12, 2025

Description:
This script runs the separate files that make up the pipeline. The order of the 
files that are run cannot be changed.

Example usage:
bash pipeline_single.sh cohort/PIm1234
'

set -e # This will make sure that this bash script will immediately end if any error occurs

patient=$1
dir_basename=$(basename $patient)
csv_file=csvs/cohort_rbc_mem_ratios.csv
rbc_m_ratio=$(awk -F',' -v name="$dir_basename" '$1 == name {print $2}' "$csv_file")

echo "Cleaning up files from previous run for patient ${dir_basename}"
bash clean_single.sh $patient

echo "START: Starting pipeline for patient: ${dir_basename}"

python -u reconstruct.py --config config/tests/cohort_master_config.py --force_recon --rbc_m_ratio $rbc_m_ratio --patient_path $patient
echo "Reconstruction finished for patient ${dir_basename}"

python -u reorient.py $patient
echo "Reorientation finished for patient ${dir_basename}, press any key to continue"

python -u resize.py $patient
echo "Resizing finished for patient ${dir_basename}, press any key to continue"

python register_single.py $patient vent 
python register_single.py $patient reg  

python -u mod_corepeel.py $patient
python -u unpack.py $patient
python -u warp_vent.py $patient
python -u stats.py --config config/tests/cohort_master_config.py --patient_path $patient
echo "Finished computing stats for patient ${dir_basename}."
echo "Pipeline completed for patient ${dir_basename}"

echo "Cleaning up intermediate files for patient ${dir_basename}"
bash clean_single.sh $patient

echo ${dir_basename} >> txt/pipeline_completed.txt
echo "PIPELINE COMPLETED: The pipeline has successfully completed for patient ${dir_basename} and the patient has been added to txt/pipeline_completed.txt"