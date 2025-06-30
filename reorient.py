# from utils.os_utils import aff2axcodes_RAS
import os
import nibabel as nib
import sys
import numpy as np

if len(sys.argv) < 2:
    print("Usage: python reorient.py <patient_dir>")
    sys.exit(1)

PATIENT_DIR = sys.argv[1]
patient = PATIENT_DIR

# these cts will not be warped or resized, only reoriented
ct_mask_paths = [
    os.path.join(patient, "CT_mask.nii"),
    os.path.join(patient, "CT_lobe_mask.nii"),
    os.path.join(patient, "ct_corepeel_mask.nii"),
]
   
# Skip reorienting CTs if they are already reoriented 
are_cts_reoriented = True
for ct in ct_mask_paths:
    if (not os.path.isfile(ct[:-4] + "_neg_affine.nii")):
        are_cts_reoriented = False
        print(f"File {ct} does not exist. Will redo reorientation of CT masks.")
        break

"""
Reorient CT mask (CT_mask.nii) 
"""
if (not are_cts_reoriented):
    for ct_mask_file in ct_mask_paths:
        print(f"reorient.py: Reorienting patient {os.path.dirname(ct_mask_file)} CT mask")
        # print(ct_mask_file)

        nib_ct = nib.load(ct_mask_file)

        aff = nib_ct.affine
        for i in range(3):
            if aff[i][i] > 0:
                aff[i][i] = -aff[i][i]

        nib_ct.set_qform(aff)
        path = ct_mask_file[:-4] + "_neg_affine.nii"
        if not os.path.exists(path):
            nib.save(img=nib_ct, filename=path)
            # print(f"Saved to {path}!")
            # print(aff2axcodes_RAS(nib_ct.affine))

        else:
            print(f"File {path} already exists.")
        
mri_type_image_paths = [
    os.path.join(patient, "mask_reg_edited.nii"),
    os.path.join(patient, "image_gas_highreso.nii"),
    os.path.join(patient, "image_gas_binned.nii"),
    os.path.join(patient, "image_gas_cor.nii"),
    os.path.join(patient, "image_rbc2gas_binned.nii"),
    os.path.join(patient, "image_rbc2gas.nii"),
    os.path.join(patient, "mask_vent.nii"),
    os.path.join(patient, "image_membrane.nii"),
    os.path.join(patient, "image_membrane2gas_binned.nii"),
    os.path.join(patient, "image_membrane2gas.nii"),
    os.path.join(patient, "image_gas_binned.nii"),
]
    
are_mri_reoriented = True
for mri in mri_type_image_paths:
    if (not os.path.isfile(mri[:-4] + "_mutated_affine.nii")):
        are_mri_reoriented = False
        print(f"File {mri} does not exist. Will redo MRI reorientation MRI type images.")
        break
    


"""
Reorient MRI (mask_reg_edited_scaled.nii) and ventilation (gas_highreso_scaled.nii)
"""
if (not are_mri_reoriented):
    for mri_file in mri_type_image_paths:
        print(
            f"reorient.py: Reorienting patient {os.path.dirname(mri_file)} ventilation and MRI"
        )

        # print(mri_file)
        nib_mr = nib.load(mri_file)
        new_aff = np.array([[0, -1, 0, 0], [0, 0, -1, 0], [-1, 0, 0, 0], [0, 0, 0, 1]])
        nib_mr.set_qform(new_aff)
        mr_path = mri_file[:-4] + "_mutated_affine.nii"

        # MRI
        if not os.path.exists(mr_path):
            nib.save(img=nib_mr, filename=mr_path)
            # print(f"Saved to {mr_path}!")
            # print(aff2axcodes_RAS(nib_mr.affine))
        else:
            print(f"File {mr_path} already exists.")