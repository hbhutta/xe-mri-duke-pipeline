
# Run reg once 

# recon -> get stats -> delete tmp files -> repeat
# we can manually set rbc_m_ratio, data_dir, etc.. using flags
python reconstruct.py --config config/tests/PIm0015_master.py --force_recon 
python warp.py --data_dir cohort/PIm0015


