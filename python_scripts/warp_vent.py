try:
    from utils.os_utils import get_subdirs, get_common_files
except ImportError as e:
    print(f"An error occurred: {e}")
import sys
import ants
import pickle
import os
from time import time

start_time = time()
BASE_DIR = sys.argv[1]
# subdir_paths = get_subdirs(dir=BASE_DIR)[0:1]
# ct_mask_file_paths = get_common_files(BASE_DIR, "CT_mask_neg_affine.nii")[0:1]
# ventilation_file_paths = get_common_files(BASE_DIR,  "gas_highreso_scaled_mutated_affine.nii")[0:1]

# testing with pim0072
ct_mask_file_paths = ["imgs/PIm0072/CT_mask_neg_affine.nii"]
mri_file_paths = ["imgs/PIm0072/mask_reg_edited_scaled_mutated_affine.nii"]
ventilation_file_paths = ["imgs/PIm0072/gas_highreso_scaled_mutated_affine.nii"]
subdir_paths = ["imgs/PIm0072"]

# assert 0 == 1


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
    return trans


for ct_mask_file, ventilation_file, subdir in zip(ct_mask_file_paths, ventilation_file_paths, subdir_paths):
    print(f"ct {ct_mask_file} | vent {
          ventilation_file} | patient {os.path.basename(subdir)}")

    with open(subdir + f"/{os.path.basename(subdir)}_reg.pkl", "rb") as file:
        mytx = pickle.load(file)
        print(mytx)

    warped_vent = warp_image(fixed=ct_mask_file, moving=ventilation_file,
                             transform_list=mytx['fwdtransforms'])
    try:
        assert warped_vent != None
    except AssertionError as e:
        print(f"warped_vent has value {
              warped_vent} and type {type(warped_vent)}")
        print(e)
        break
    try:
        print(type(warped_vent))
        filename = f"{subdir}/{os.path.basename(subdir)}_warped_vent.nii"
        ants.image_write(image=warped_vent, filename=filename)
    except AttributeError as e:
        print(warped_vent)

end_time = time()
print(f"That took: {end_time - start_time} mins/seconds")
