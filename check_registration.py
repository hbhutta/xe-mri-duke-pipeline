'''
This file extracts the gzipped warped mask_reg_edited from 
'''


import pickle
import os
import ants 
data_dir = "cohort/PIm0015"

with open(f"{data_dir}/{os.path.basename(data_dir)}_reg.pkl", "rb") as file:
    reg = pickle.load(file)
    warped_proton = reg['warpedmovout']
    dst = f"{data_dir}/warped_mri.nii.gz"
    ants.image_write(image=warped_proton, filename=dst)
