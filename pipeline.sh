#!/bin/bash

csv_file=cohort_rbc_mem_ratios.csv

set -ex # Exit the pipeline if any command fails

# All patients must have resized, reoriented mask_reg_edited before registration
for patient in cohort/*; do
  if [[ -d $patient ]]; then
    dir_basename=$(basename $patient)
    rbc_m_ratio=$(awk -F',' -v name="$dir_basename" '$1 == name {print $2}' "$csv_file")
    python -u reconstruct.py --config config/tests/cohort_master_config.py --force_recon --rbc_m_ratio $rbc_m_ratio --patient_path $patient
    python -u reorient.py $patient
    python -u resize.py $patient
    printf "\n\n\nFinished reconstructions, reorienting and resizing for patient ${dir_basename}\n\n\n"
  fi
done

python register.py # requires reoriented and resized mask_reg_edited

for patient in cohort/*; do
  if [[ -d $patient ]]; then
    python -u mod_corepeel.py $patient
    python -u unpack.py $patient
    python -u warp_vent.py $patient
    python -u stats.py --config config/tests/cohort_master_config.py --patient_path $patient
    bash clean.sh $patient # clean files no longer needed in this dir to save space
  fi
done  


