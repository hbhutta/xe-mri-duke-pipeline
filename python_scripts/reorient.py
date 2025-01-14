from utils.os_utils import aff2axcodes_RAS 
import os
import nibabel as nib
from time import time
from sys import argv
import numpy as np

prep_start_time = time()

BASE_DIR = argv[1]

# Assuming each patient has these files
#subdir_paths = get_subdirs(dir=BASE_DIR)[0:1]
#ct_mask_file_paths = get_common_files(
#    base_dir=BASE_DIR, filename='CT_mask.nii')[0:1]
#mri_file_paths = get_common_files(
#    base_dir=BASE_DIR, filename='mask_reg_edited_scaled.nii')[0:1]
#ventilation_file_paths = get_common_files(
#    base_dir=BASE_DIR, filename='gas_highreso_scaled.nii')[0:1]

ct_mask_file_paths = ["imgs/PIm0072/CT_mask.nii"]
#ct_mask_file_paths = ["./CT_mask.nii"]
mri_file_paths = ["imgs/PIm0072/mask_reg_edited_scaled.nii"]
ventilation_file_paths = ["imgs/PIm0072/gas_highreso_scaled.nii"]
subdir_paths = ["imgs/PIm0072"]
#subdir_paths=["."]

# print(ct_mask_file_paths)
# print(mri_file_paths)
# print(ventilation_file_paths)

"""
Reorient CT mask (CT_mask.nii) 
"""
for ct_mask_file, subdir in zip(ct_mask_file_paths, subdir_paths):
    print(f"reorient.py: Reorienting patient {os.path.basename(subdir)} CT mask")
    print(ct_mask_file)

    nib_ct = nib.load(ct_mask_file)

    aff = nib_ct.affine
    for i in range(3):
        if (aff[i][i] > 0):
            aff[i][i] = -aff[i][i]

    nib_ct.set_qform(aff)
    path = ct_mask_file[:-4] + '_neg_affine.nii'
    if not os.path.exists(path):
        nib.save(img=nib_ct, filename=path)
        print(f"Saved to {path}!")
        print(aff2axcodes_RAS(nib_ct.affine))

    else:
        print(f"File {path} already exists.")
print("done ct reorienting")
#assert 0 == 1

"""
Reorient MRI (mask_reg_edited_scaled.nii) and Ventilation (gas_highreso_scaled.nii)
"""
for mri_file, vent_file, subdir in zip(mri_file_paths, ventilation_file_paths, subdir_paths):
    print(f"reorient.py: Reorienting patient {os.path.basename(subdir)} ventilation and MRI")

    print(mri_file)
    print(vent_file)

    nib_mr = nib.load(mri_file)
    nib_vent = nib.load(vent_file)

    aff = nib_mr.affine
    new_aff = np.array([[0, -1, 0, 0],
                        [0, 0, -1, 0],
                        [-1, 0, 0, 0],
                        [0, 0, 0, 1]])

    nib_mr.set_qform(new_aff)
    nib_vent.set_qform(new_aff)

    mr_path = mri_file[:-4] + '_mutated_affine.nii'
    vent_path = vent_file[:-4] + '_mutated_affine.nii'

    # MRI
    if not os.path.exists(mr_path):
        nib.save(img=nib_mr, filename=mr_path)
        print(f"Saved to {mr_path}!")
        print(aff2axcodes_RAS(nib_mr.affine))
    else:
        print(f"File {mr_path} already exists.")

    # Ventilation
    if not os.path.exists(vent_path):
        nib.save(img=nib_vent, filename=vent_path)
        print(f"Saved to {vent_path}!")
        print(aff2axcodes_RAS(nib_vent.affine))
    else:
        print(f"File {vent_path} already exists.")

prep_end_time = time()
print(f"That took: {prep_end_time - prep_start_time} min/sec")
