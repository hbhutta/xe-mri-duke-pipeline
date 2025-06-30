import ants
import pickle
import os
from time import time
from sys import argv

start_time = time()

patient_path = argv[1]

imgs = [
    #    [os.path.join(patient, "mask_reg_edited_mutated_affine_resized.nii") for patient in patients],
    os.path.join(patient_path, "image_gas_highreso_mutated_affine_resized.nii"),
    os.path.join(patient_path, "image_gas_binned_mutated_affine_resized.nii"),
    os.path.join(patient_path, "image_gas_cor_mutated_affine_resized.nii"),
    os.path.join(patient_path, "image_rbc2gas_binned_mutated_affine_resized.nii"),
    os.path.join(patient_path, "image_rbc2gas_mutated_affine_resized.nii"),
    #    [os.path.join(patient, "mask_vent_mutated_affine_resized.nii") for patient in patients],
    os.path.join(patient_path, "image_membrane_mutated_affine_resized.nii"),
    os.path.join(patient_path, "image_membrane2gas_binned_mutated_affine_resized.nii"),
    os.path.join(patient_path, "image_membrane2gas_mutated_affine_resized.nii"),
    os.path.join(patient_path, "image_gas_binned_mutated_affine_resized.nii"),
]

print(imgs)
# assert 0 == 1
# Haad: We shouldn't have a default argument for the interpolator as we have different types of images above; some are binned (discrete) and some are "continuous"  / not binned.
# Haad: This function is not being used, but I will keep it here for reference.
# def apply_fwdtranforms(ANTS_CT, ANTS_Vent, transformlist):
#     trans = ants.apply_transforms(
#         fixed=ANTS_CT,
#         moving=ANTS_Vent,
#         transformlist=transformlist,
#         interpolator="multiLabel",
#         imagetype=0,
#         whichtoinvert=None,
#         compose=None,
#         defaultvalue=0,
#         verbose=True,
#     )
#     return trans

def warp_image(
    fixed, moving, transform_list, interpolator
):  # UNDO, make multiLabel the default
    """
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

    """
    ants_fixed = ants.image_read(fixed)
    ants_moving = ants.image_read(moving)

    trans = ants.apply_transforms(
        fixed=ants_fixed,
        moving=ants_moving,
        transformlist=transform_list,
        interpolator=interpolator, # Haad: I changed this to multilabel, I don't want to use a default interpolator as this might easily change in different cases
        imagetype=0,
        whichtoinvert=None,
        # compose=None,
        defaultvalue=0,
        verbose=True,
    )
    if interpolator in ["nearestNeighbor", "multiLabel", "genericLabel"]:
        trans[trans < 1] = 0

    assert trans is not None
    ants.image_write(image=trans, filename=moving[:-4] + "_warped.nii")


# with open(f"{PATIENT}/{os.path.basename(patient_path)}_reg.pkl", "rb") as file:
#     mytx = pickle.load(file)

with open(os.path.join(patient_path, f"{os.path.basename(patient_path)}_reg.pkl"), "rb") as file:
    mytx = pickle.load(file=file)

FIXED_IMG = os.path.join(patient_path, "CT_mask_neg_affine.nii")
for img in imgs:
    if not os.path.isfile(img[:-4] + "_warped.nii"):
        
        # Haad: Here we will change the interpolator based on whether the image is binned or not, with the hope that this will resolve the image_cor NaN's in image error
        
        ################################################# 
        interpolator = "linear"
        if "binned" in img:
            interpolator = "multiLabel"
        ################################################# 

        warp_image(
            fixed=FIXED_IMG,
            moving=img,
            transform_list=mytx["fwdtransforms"],
            interpolator=interpolator
        )
    else:
        print(f"File {img} already warped")