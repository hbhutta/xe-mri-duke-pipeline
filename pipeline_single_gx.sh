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

set -euo pipefail # This will make sure that this bash script will immediately end if any error occurs

patient=$1
dir_basename=$(basename $patient)

if [[ -f "${patient}/${dir_basename}_stats.csv" ]]; then
    echo "Pipeline has already been run for patient ${dir_basename}. Skipping."
    exit 0
fi

rbc_mem_ratios=csvs/cohort_rbc_mem_ratios.csv
rbc_m_ratio=$(awk -F',' -v name="$dir_basename" '$1 == name {print $2}' "$rbc_mem_ratios")

hb_correction_values=csvs/cohort_hb_corrections.csv
hb_correction_value=$(awk -F',' -v name="$dir_basename" '$1 == name {print $2}' "$hb_correction_values")

echo "Cleaning up files from previous run for patient ${dir_basename}"
bash clean_single.sh $patient

echo "START: Starting pipeline for patient: ${dir_basename}"

python -u reconstruct.py --config config/master_config.py --force_recon --rbc_m_ratio $rbc_m_ratio --hb $hb_correction_value --patient_path $patient 
echo "Reconstruction finished for patient ${dir_basename}"

python -u reorient.py --config config/master_config.py --patient_path $patient
echo "Reorientation finished for patient ${dir_basename}"

python -u resize.py --config config/master_config.py --patient_path $patient
echo "Resizing finished for patient ${dir_basename}"

python register_single.py --config config/master_config.py --patient_path $patient --vent_or_reg vent
python register_single.py --config config/master_config.py --patient_path $patient --vent_or_reg reg

python -u mod_corepeel.py --config config/master_config.py --patient_path $patient
python -u unpack.py --config config/master_config.py --patient_path $patient
python -u warp_vent.py --config config/master_config.py --patient_path $patient

if [[ -f "${patient}/CT_sublobe_mask.nii" ]]; then
    echo "Sublobe mask found for patient ${dir_basename}. Computing sublobe stats."
    python -u stats_lobe.py --config config/master_config.py --patient_path $patient --sublobe
    python -u rename_csv.py --config config/master_config.py --patient_path $patient --sublobe
else
    echo "No sublobe mask found for patient ${dir_basename}. Skipping sub lobe stats."
    python -u stats_lobe.py --config config/master_config.py --patient_path $patient   
    python -u rename_csv.py --config config/master_config.py --patient_path $patient
fi

echo "Finished computing stats for patient ${dir_basename}."
echo "Pipeline completed for patient ${dir_basename}"

bash clean_single_end.sh $patient