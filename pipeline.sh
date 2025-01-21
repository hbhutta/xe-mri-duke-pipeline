#!/bin/bash

python reconstruct.py --config config/tests/cohort_master_config.py --force_recon 
python reorient.py
python resize.py
python register.py
python unpack.py
python warp_vent.py
python stats.py --config config/tests/cohort_master_config.py




