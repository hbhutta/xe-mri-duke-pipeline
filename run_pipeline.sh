
# Run reg once 
python register.py 

# recon -> get stats -> delete tmp files -> repeat
# we can manually set rbc_m_ratio, data_dir, etc.. using flags
for patient_dir in cohort/*; do
    if [[ -d $patient_dir ]]; then
    python reconstruct.py --config config/tests/PIm02_master.py \
    --data_dir $patient_dir \
    --subject_id $(basename $patient_dir) \
    --rbc_m_ratio = 
    --force_recon 

    fi
done
python reconstruct.py --config config/tests/PIm02_master.py --force_recon 
python stats.py --
wait


