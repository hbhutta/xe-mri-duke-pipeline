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

# read -p "Clean up files from previous run? [Y/N]" cleanup
# if [[ $cleanup=="Y" ]]; then
#     bash clean_single.sh $patient
# elif [[ $cleanup=="N" ]]; then
#     echo "Clean up skipped, proceeding with existing registration"
# else
#     echo "Invalid option, try again or exit the pipeline."
#     exit 1
# fi
bash clean_single.sh $patient

# read -p "Redo reconstruction? [Y/N]" redo_recon
# if [[ $redo_recon=="Y" ]]; then
#     echo "Read rbc-membrane ratio of ${rbc_m_ratio}. Starting reconstruction."
#     python -u reconstruct.py --config config/tests/cohort_master_config.py --force_recon --rbc_m_ratio $rbc_m_ratio --patient_path $patient
#     echo "Reconstruction finished for patient ${dir_basename}"
# elif [[ $redo_recon=="N" ]]; then
#     echo "Reconstruction skipped, proceeding with existing registration"
# else
#     echo "Invalid option, try again or exit the pipeline."
#     exit 1
# fi


# 
python -u reconstruct.py --config config/tests/cohort_master_config.py --force_recon --rbc_m_ratio $rbc_m_ratio --patient_path $patient
echo "Reconstruction finished for patient ${dir_basename}"
# read -p "Press any key to continue"

python -u reorient.py $patient
echo "Reorientation finished for patient ${dir_basename}, press any key to continue"
# read -p "Press any key to continue"

python -u resize.py $patient
echo "Resizing finished for patient ${dir_basename}, press any key to continue"
# read -p "Press any key to continue"

# Haad: The vent param to register_single.py indicates that mask_vent is being registered to the (reoriented) CT_mask, while the reg param indicates that mask_reg_edited is being registered. 
# We need to register both mask_vent and mask_reg_edited to the reoriented CT_mask separately because when computing the statistics in the get_statistics() function in subject_classmap.py, some of stats rely on mask_vent while others rely on mask_reg_edited. For example, the RBC and membrane binned percentages rely on mask_vent while the ventilation binned percentages rely on mask_reg_edited.

# What is the difference between these two?
python register_single.py $patient vent # requires reoriented and resized mask_vent
python register_single.py $patient reg  # requires reoriented and resized mask_reg_edited

python -u mod_corepeel.py $patient
python -u unpack.py $patient
python -u warp_vent.py $patient
python -u stats.py --config config/tests/cohort_master_config.py --patient_path $patient
echo "Finished computing stats for patient ${dir_basename}."
echo "Pipeline completed for patient ${dir_basename}"
