import os
from sys import argv
import nibabel as nib

BASE_DIR = argv[1] # patient path
print(f"mod_corepeel.py: recieved BASE_DIR: {BASE_DIR}")

ct_mask_path = os.path.join(BASE_DIR, "CT_mask_neg_affine.nii")
#ct_corepeel_mask_path = os.path.join(BASE_DIR, "ct_corepeel_mask.nii")

ct_mask = nib.load(ct_mask_path)

q, px, py, pz = ct_mask.header["pixdim"][0:4]

qoffset_x = ct_mask.header["qoffset_x"]
qoffset_y = ct_mask.header["qoffset_y"]
qoffset_z = ct_mask.header["qoffset_z"]

# Modify origin (qoffsets) and pixdims (voxel size)
os.system(f"nifti_tool -mod_hdr -mod_field pixdim '{q} {px} {py} {pz} 0.0 0.0 0.0 0.0' -prefix {BASE_DIR}/ct_corepeel_mask_neg_affine_mod.nii -infiles {BASE_DIR}/ct_corepeel_mask_neg_affine.nii")
os.system(f"nifti_tool -mod_hdr -mod_field qoffset_x {qoffset_x} -prefix {BASE_DIR}/ct_corepeel_mask_neg_affine_mod_x.nii -infiles {BASE_DIR}/ct_corepeel_mask_neg_affine_mod.nii")
os.system(f"nifti_tool -mod_hdr -mod_field qoffset_y {qoffset_y} -prefix {BASE_DIR}/ct_corepeel_mask_neg_affine_mod_x_y.nii -infiles {BASE_DIR}/ct_corepeel_mask_neg_affine_mod_x.nii")
os.system(f"nifti_tool -mod_hdr -mod_field qoffset_z {qoffset_z} -prefix {BASE_DIR}/ct_corepeel_mask_neg_affine_mod_x_y_z.nii -infiles {BASE_DIR}/ct_corepeel_mask_neg_affine_mod_x_y.nii")

# Delete intermediate files 
os.remove(f"{BASE_DIR}/ct_corepeel_mask_neg_affine_mod.nii")
os.remove(f"{BASE_DIR}/ct_corepeel_mask_neg_affine_mod_x.nii")
os.remove(f"{BASE_DIR}/ct_corepeel_mask_neg_affine_mod_x_y.nii")
