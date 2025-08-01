import ants
import pickle
import os

from absl import app, flags
from ml_collections import config_flags

FLAGS = flags.FLAGS
_CONFIG = config_flags.DEFINE_config_file("config", None, "config file.")

flags.DEFINE_string(
    name="patient_path",
    default=None,  # assuming that this is where .dat files are stored by default
    help="The folder where the .dat files are stored",
    required=True,
)

def warp_image(
    fixed, moving, transform_list, interpolator
):  
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

def warp_images(patient_path: str) -> None:
    with open(os.path.join(patient_path, f"{os.path.basename(patient_path)}_reg.pkl"), "rb") as file:
        mytx = pickle.load(file=file)

    FIXED_IMG = os.path.join(patient_path, "CT_mask_neg_affine.nii")
    
    processed_image_names = [
        "image_gas_highreso_mutated_affine_resized.nii",
        "image_gas_binned_mutated_affine_resized.nii",
        "image_gas_cor_mutated_affine_resized.nii",
        "image_rbc2gas_binned_mutated_affine_resized.nii",
        "image_rbc2gas_mutated_affine_resized.nii",
        "image_membrane_mutated_affine_resized.nii",
        "image_membrane2gas_binned_mutated_affine_resized.nii",
        "image_membrane2gas_mutated_affine_resized.nii",
        "image_gas_binned_mutated_affine_resized.nii",
    ]
    
    processed_image_paths = [os.path.join(patient_path, name) for name in processed_image_names]
    
    for image_path in processed_image_paths:
        if not os.path.isfile(image_path[:-4] + "_warped.nii"):

            # Haad: Here we will change the interpolator based on whether the image is binned or not, with the hope that this will resolve the image_cor NaN's in image error
            ################################################# 
            interpolator = "linear"
            if "binned" in image_path:
                interpolator = "multiLabel"
            ################################################# 

            warp_image(
                fixed=FIXED_IMG,
                moving=image_path,
                transform_list=mytx["fwdtransforms"],
                interpolator=interpolator
            )
        else:
            print(f"warp_vent.py, warp_images(): File {image_path} already warped") 

def main(argv):
    config = _CONFIG.value
    config.data_dir = FLAGS.patient_path
    patient_path = config.data_dir
    warp_images(patient_path)
   
if __name__ == "__main__": 
    app.run(main)