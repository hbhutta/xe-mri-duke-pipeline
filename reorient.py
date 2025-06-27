from utils.os_utils import aff2axcodes_RAS
import os
import nibabel as nib
from time import time
import sys
import numpy as np

prep_start_time = time()

# import sys

if len(sys.argv) < 2:
    print("Usage: python reorient.py <patient_dir>")
    sys.exit(1)

BASE_DIR = sys.argv[1]

patients = [BASE_DIR]

# these cts will not be warped or resized, only reoriented
cts = [
    [os.path.join(patient, "CT_mask.nii") for patient in patients],
    [os.path.join(patient, "CT_lobe_mask.nii") for patient in patients],
    [os.path.join(patient, "ct_corepeel_mask.nii") for patient in patients],
]

ct_mask_img_paths = []
for ct in cts:
    ct_mask_img_paths += ct

print(ct_mask_img_paths)

imgs = [
    [os.path.join(patient, "mask_reg_edited.nii") for patient in patients],
    [os.path.join(patient, "image_gas_highreso.nii") for patient in patients],
    [os.path.join(patient, "image_gas_binned.nii") for patient in patients],
    [os.path.join(patient, "image_gas_cor.nii") for patient in patients],
    [os.path.join(patient, "image_rbc2gas_binned.nii") for patient in patients],
    [os.path.join(patient, "image_rbc2gas.nii") for patient in patients],
    [os.path.join(patient, "mask_vent.nii") for patient in patients],
    [os.path.join(patient, "image_membrane.nii") for patient in patients],
    [os.path.join(patient, "image_membrane2gas_binned.nii") for patient in patients],
    [os.path.join(patient, "image_membrane2gas.nii") for patient in patients],
    [os.path.join(patient, "image_gas_binned.nii") for patient in patients],
    
    # Haad: We need to apply fwdtransforms to RGB images later, so they need to be preprocessed (i.e. resized and reoriented)
    [os.path.join(patient, "image_gas_binned_rgb.nii") for patient in patients],
    [os.path.join(patient, "image_membrane2gas_binned_rgb.nii") for patient in patients],
    [os.path.join(patient, "image_rbc2gas_binned_rgb.nii") for patient in patients],
]

mri_img_paths = []
for arr in imgs:
    mri_img_paths += arr

print(mri_img_paths)

# gas_file_paths = [os.path.join(patient, "gas_binned.nii") for patient in patient_paths]
# mem_file_paths = [os.path.join(patient, "membranegas_binned.nii") for patient in patient_paths]
# rbc_file_paths = [os.path.join(patient, "rbc2gas_binned.nii") for patient in patient_paths]

# assert len(ct_mask_file_paths) == len(patient_paths)
# assert len(mri_file_paths) == len(patient_paths)


"""
Reorient CT mask (CT_mask.nii) 
"""
for ct_mask_file in ct_mask_img_paths:
    print(f"reorient.py: Reorienting patient {os.path.dirname(ct_mask_file)} CT mask")
    print(ct_mask_file)

    nib_ct = nib.load(ct_mask_file)

    aff = nib_ct.affine
    for i in range(3):
        if aff[i][i] > 0:
            aff[i][i] = -aff[i][i]

    nib_ct.set_qform(aff)
    path = ct_mask_file[:-4] + "_neg_affine.nii"
    if not os.path.exists(path):
        nib.save(img=nib_ct, filename=path)
        print(f"Saved to {path}!")
        print(aff2axcodes_RAS(nib_ct.affine))

    else:
        print(f"File {path} already exists.")
print("done ct reorienting")
# assert 0 == 1

"""
Reorient MRI (mask_reg_edited_scaled.nii) and Ventilation (gas_highreso_scaled.nii)
"""
for mri_file in mri_img_paths:
    print(
        f"reorient.py: Reorienting patient {os.path.dirname(mri_file)} ventilation and MRI"
    )

    print(mri_file)

    nib_mr = nib.load(mri_file)

    new_aff = np.array([[0, -1, 0, 0], [0, 0, -1, 0], [-1, 0, 0, 0], [0, 0, 0, 1]])

    nib_mr.set_qform(new_aff)

    mr_path = mri_file[:-4] + "_mutated_affine.nii"

    # MRI
    if not os.path.exists(mr_path):
        nib.save(img=nib_mr, filename=mr_path)
        print(f"Saved to {mr_path}!")
        print(aff2axcodes_RAS(nib_mr.affine))
    else:
        print(f"File {mr_path} already exists.")

prep_end_time = time()
print(f"That took: {prep_end_time - prep_start_time} min/sec")
