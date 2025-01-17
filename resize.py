from scipy.ndimage import zoom
import numpy as np
from nibabel.nifti1 import Nifti1Image
import nibabel as nib 
import skimage.transform as skTrans
import os
import ants 
import cv2
"""
Scales the given image's data matrix
"""
def adjust_scaling(data, factor):   
    return zoom(data, factor)

"""
To account for fractional and negative pixel intensities caused by zooming
"""
def adjust_contrast(data):
    process = np.where(data > 1, 1, data) # p >= 1 -> 1
    process = np.where(data < 0, 0, data) # p < 0 -> 0
    process = np.where(np.all(data) > 0 & np.all(data) < 1, 0, data) # 0 < p < 1 -> 0
    return process

def resize(img_path: str) -> None:
    img = nib.load(img_path) 
    data = img.get_fdata()
    scaled_data = adjust_scaling(data=data, factor=(2,2,2))
    # contrast_adjusted_data = adjust_contrast(data=scaled_data)
    scaled_img = Nifti1Image(dataobj=scaled_data, affine=img.affine) 
    nib.save(scaled_img, img_path[:-4] + "_scaled_new.nii")

def foo(path):
    im = nib.load(path)
    data = im.get_fdata()
    res = skTrans.resize(data, (512,512,368), order=1, preserve_range=True)
    nib.save(Nifti1Image(dataobj=res, affine=im.affine), path[:-4] + "_scaled.nii")



#grow_cmd = f"nifti_tool -mod_hdr -prefix {temp_target[:-4]}_grown.nii -infiles {temp_target} -mod_field dim '3 {dx} {dy} {dz} 1 1 1 1'"
    
ct_mask = "cohort/PIm0015/CT_mask_neg_affine.nii" 
mri = "cohort/PIm0015/mask_reg_edited.nii" 


def resize(img_to_resize: str):
    nib_res = nib.load(img_to_resize)
    
    res_qfac = nib_res.header['pixdim'][0]
    px = nib_res.header["pixdim"][1]
    py = nib_res.header["pixdim"][2]
    pz = nib_res.header["pixdim"][3]
    
    img_to_resize = ants.image_read(filename=img_to_resize)

    resampled = ants.resample_image(image=img_to_resize, resample_params=(512, 512, 512), use_voxels=True)

    resized_fname = img_to_resize[:-4] + "_resized.nii"
    ants.image_write(resampled, resized_fname)

    new_fname = resized_fname[:-4] + "_set_px.nii"

    set_pixdim_cmd = f"nifti_tool -mod_hdr -prefix {new_fname} -infiles {resized_fname} -mod_field pixdim '{res_qfac} {px} {py} {pz} 0.0 0.0 0.0 0.0'"
    os.system(set_pixdim_cmd)
     

resize(mri)


# nib_mri = nib.load(mri)

# print(nib_mri.header)
# print('\n\n\n\n\n')

# mri_qfac = nib_mri.header['pixdim'][0]
# px = nib_mri.header["pixdim"][1]
# py = nib_mri.header["pixdim"][2]
# pz = nib_mri.header["pixdim"][3]
# print(px,py,pz)
# print('\n\n\n\n\n')


# img_to_resample = ants.image_read(filename=mri)
# img_of_reference = ants.image_read(filename=ct_mask)

# resampled = ants.resample_image(image=img_to_resample, resample_params=(512, 512, 512), use_voxels=True)

# resampled_mri_fname = mri[:-4] + "_resampled.nii"
# ants.image_write(resampled, resampled_mri_fname)

# new_mri_fname = resampled_mri_fname[:-4] + "_set_px.nii"

# set_pixdim_cmd = f"nifti_tool -mod_hdr -prefix {new_mri_fname} -infiles {resampled_mri_fname} -mod_field pixdim '{mri_qfac} {px} {py} {pz} 0.0 0.0 0.0 0.0'"
# os.system(set_pixdim_cmd)

# nib_new_mri = nib.load(new_mri_fname)
# print(nib_new_mri.header)


