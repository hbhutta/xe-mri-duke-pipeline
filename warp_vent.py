# try:
#     from utils.os_utils import get_subdirs, get_common_files
# except ImportError as e:
#     print(f"An error occurred: {e}")
# import sys
import ants
import pickle
import os
from time import time
from sys import argv


start_time = time()

patients = [argv[1]]

imgs = [
#    [os.path.join(patient, "mask_reg_edited_mutated_affine_resized.nii") for patient in patients],
    [os.path.join(patient, "image_gas_highreso_mutated_affine_resized.nii") for patient in patients],
    [os.path.join(patient, "image_gas_binned_mutated_affine_resized.nii") for patient in patients],
    [os.path.join(patient, "image_gas_cor_mutated_affine_resized.nii") for patient in patients],
    [os.path.join(patient, "image_rbc2gas_binned_mutated_affine_resized.nii") for patient in patients],
    [os.path.join(patient, "image_rbc2gas_mutated_affine_resized.nii") for patient in patients],
#    [os.path.join(patient, "mask_vent_mutated_affine_resized.nii") for patient in patients],
    [os.path.join(patient, "image_membrane_mutated_affine_resized.nii") for patient in patients],
    [os.path.join(patient, "image_membrane2gas_binned_mutated_affine_resized.nii") for patient in patients],
    [os.path.join(patient, "image_membrane2gas_mutated_affine_resized.nii") for patient in patients],
    [os.path.join(patient, "image_gas_binned_mutated_affine_resized.nii") for patient in patients]
]

mri_img_paths = []
for arr in imgs:
    mri_img_paths += arr


def apply_fwdtranforms(ANTS_CT, ANTS_Vent, transformlist):
    trans = ants.apply_transforms(fixed=ANTS_CT, moving=ANTS_Vent,
                                  transformlist=transformlist,
                                  interpolator='linear', imagetype=0,
                                  whichtoinvert=None, compose=None,
                                  defaultvalue=0, verbose=True)
    return trans


def warp_image(fixed, moving, transform_list, interpolation='linear'):
    '''
    Use transforms from registration process to warp an image to target.  For example, if you register the ventilation mask to the CT mask,
    you can use the transforms to warp the ventilation intensity image to the CT space.    

    Parameters
    ----------
    moving : str
        path to fixed image defining domain into which the moving image is transformed
    fixed : str
        path to target image.
    transform_list : list
        list of transforms ***in following order*** [1Warp.nii.gz,0GenericAffine.mat] 
    interpolation : str
            linear (default)
            nearestNeighbor
            multiLabel for label images but genericlabel is preferred
            gaussian
            bSpline
            cosineWindowedSinc
            welchWindowedSinc
            hammingWindowedSinc
            lanczosWindowedSinc
            genericLabel use this for label images

    Returns
    -------
    image warped to target image.

    '''
    ants_fixed = ants.image_read(fixed)
    ants_moving = ants.image_read(moving)

    trans = ants.apply_transforms(fixed=ants_fixed,
                                  moving=ants_moving,
                                  transformlist=transform_list,
                                  interpolator=interpolation,
                                  imagetype=0,
                                  whichtoinvert=None,
                                  # compose=None,
                                  defaultvalue=0, verbose=True)
    if interpolation in ['nearestNeighbor', 'multiLabel', 'genericLabel']:
        trans[trans < 1] = 0
        
    assert trans is not None
    ants.image_write(image=trans, filename=moving[:-4] + "_warped.nii")


PATIENT = patients[0]
with open(f"{PATIENT}/{os.path.basename(PATIENT)}_reg.pkl", "rb") as file:
    mytx = pickle.load(file)

for img in mri_img_paths:
    if (not os.path.isfile(img[:-4] + "_warped.nii")):
        warp_image(fixed=os.path.join(os.path.dirname(img), "CT_mask_neg_affine.nii"), moving=img, transform_list=mytx['fwdtransforms'])
    else:
        print(f"File {img} already warped")

