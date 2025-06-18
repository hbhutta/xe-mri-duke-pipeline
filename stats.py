"""Scripts to run gas exchange mapping pipeline."""

import pickle
import nibabel as nib
import numpy as np

from utils.img_utils import split_mask

# import dask.array as da

from absl import app, flags
from ml_collections import config_flags

from config import base_config
from subject_classmap import Subject

import os

FLAGS = flags.FLAGS

_CONFIG = config_flags.DEFINE_config_file("config", None, "config file.")

flags.DEFINE_string(
    name="patient_path",
    default=None,  # assuming that this is where .dat files are stored by default
    help="The folder where the .dat files are stored",
    required=True,
)


def make_bool(data: np.ndarray):
    process = np.where(np.abs(data - 1) < np.abs(data - 0), 1, 0)
    return process


def basename(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def compute_split_product(img_path: str, split_path: str) -> str:
    if not os.path.isfile(img_path):
        raise FileNotFoundError(f"File {img_path} does not exist")
    new_img_path = os.path.join(
        os.path.dirname(img_path),
        f"{basename(img_path)}__{basename(split_path)}_product.nii",
    )
    cmd = f"./bin/c3d -verbose {img_path} {split_path} -multiply -o {new_img_path}"
    os.system(cmd)
    return new_img_path


def compute_patient_stats(config: base_config.Config):
    """Compute statistics for the patient

    Computing statistics in get_statistics() uses specific images:
    - self.image_gas_binned
    - self.image_membrane2gas_binned
    - self.image_rbc2gas_binned
    - self.image_rbc2gas
    - self.image_membrane2gas
    - self.image_gas_cor
    - self.mask
    - self.mask_vent

    Note that these attributes are of type np.ndarray.

    To get the np.ndarray of a NIFTI image called 'img' we can do this:

    img = nib.load(img_path)
    img_data = img.get_fdata()

    If registration is done by this point and these images are warped
    based on the fwdtransforms, we can apply the CT mask splits
    (e.g. core, peel, five lobes) and run the functions:
    - subject.get_statistics()
    - subject.write_stats_to_csv()

    We have to apply the forward transforms from registration onto
    the images above before applying the mask

    We may want to use ANTS functions to read/write images
    instead of nibabel functions because we will ultimately use
    antsApplyTransform to apply the forward transforms to the images

    For each of:
    - Core
    - Peel
    - RUL (right upper lobe)
    - RLL (right lower lobe)
    - RML (right middle lobe)
    - LLL (left lower lobe)
    - LUL (left upper lobe)

    We shouldn't overwrite the csv at every call to write_stats_to_csv

    The outer for-loop loops over every split.
    The inner for loops loops over every relevant image.

    ANTS functions of interest are:
    - numpy(): to get underlying data for image
        - if this doesn't work, we can nib.load then get_fdata
    - mask_image(target, mask): applies mask to target, both ANTS images
    - image_read(filename): reads an ANTS image from a filename

    fwdtransforms only need to be applied once, its doesn't depend on a split

    Args:
        config (config_dict.ConfigDict): config dict
    """

    subject = Subject(config=config)

    """
    After resizing, will have _resized.nii ending
    After warping, will have _warped.nii ending
    """
    # imgs = [
    #     "mask_reg_edited.nii",
    #     "image_gas_highreso.niiimage_gas_binned.nii",
    #     "image_gas_cor.nii",
    #     "image_rbc2gas_binned.nii",
    #     "image_rbc2gas.nii",
    #     "mask_vent.nii",
    #     "image_membrane.nii",
    #     "image_membrane2gas_binned.nii",
    #     "image_membrane2gas.nii",
    #     "image_gas_binned.nii",
    # ]

    masks = ["CT_lobe_mask_neg_affine.nii", "ct_corepeel_mask_neg_affine_mod_x_y_z.nii"]
    masks = [os.path.join(f"{subject.config.data_dir}", mask) for mask in masks]

    splits = []
    for mask in masks:
        splits += split_mask(mask)
       
    splits_dict = {
        "left_upper_lobe": [],
        "left_lower_lobe": [],
        "right_upper_lobe": [],
        "right_middle_lobe": [],
        "right_lower_lobe": [],
        "core": [],
        "peel": [],
        "whole_lung": []
    }
    
    # This line alone will ensure stats are computed for the whole lung
    """
    Haad: This line should be after the for loop that splits the masks
    into the core, peel, five lobes, etc.. because the CT_mask should not be # split

    """
    splits.append(os.path.join(f"{subject.config.data_dir}", "CT_mask_neg_affine.nii"))
    
    pixel_intensities = [8, 16, 32, 64, 128, 40, 50, 1]
    assert len(pixel_intensities) == len(splits)
    
    i = 0  
    for k in splits_dict.keys():
        splits_dict[k].append(splits[i]) # First element of value is the split path (string)
        splits_dict[k].append(pixel_intensities[i]) # Second element of value is the pixel intensity (int)
        i += 1

    """
    Haad:
    Initializing the image data used in computing the bin percentages
    can be outside the for loop that processes the splits because
    these do not depend on the splits. 
    """
    subject.image_gas_highreso = nib.load(
        os.path.join(
            subject.config.data_dir,
            "image_gas_highreso_mutated_affine_resized_warped.nii",
        )
    ).get_fdata()
    subject.image_gas_binned = nib.load(
        os.path.join(
            subject.config.data_dir,
            "image_gas_binned_mutated_affine_resized_warped.nii",
        )
    ).get_fdata()
    subject.image_gas_cor = nib.load(
        os.path.join(
            subject.config.data_dir,
            "image_gas_cor_mutated_affine_resized_warped.nii",
        )
    ).get_fdata()
    subject.image_rbc2gas_binned = nib.load(
        os.path.join(
            subject.config.data_dir,
            "image_rbc2gas_binned_mutated_affine_resized_warped.nii",
        )
    ).get_fdata()
    subject.image_rbc2gas = nib.load(
        os.path.join(
            subject.config.data_dir,
            "image_rbc2gas_mutated_affine_resized_warped.nii",
        )
    ).get_fdata()
    subject.image_membrane = nib.load(
        os.path.join(
            subject.config.data_dir,
            "image_membrane_mutated_affine_resized_warped.nii",
        )
    ).get_fdata()
    subject.image_membrane2gas_binned = nib.load(
        os.path.join(
            subject.config.data_dir,
            "image_membrane2gas_binned_mutated_affine_resized_warped.nii",
        )
    ).get_fdata()
    subject.image_membrane2gas = nib.load(
        os.path.join(
            subject.config.data_dir,
            "image_membrane2gas_mutated_affine_resized_warped.nii",
        )
    ).get_fdata()
    subject.image_gas_binned = nib.load(
        os.path.join(
            subject.config.data_dir,
            "image_gas_binned_mutated_affine_resized_warped.nii",
        )
    ).get_fdata()


    for split in splits:
        print(f"Processing split {split}")
        subject.mask = np.where(nib.load(split).get_fdata() > 0.5, 1, 0)

        """
        Haad:
        These lines compute the intersection between the current split and the mask.
        The mask_vent attribute of this subject is set to the product (intersection)
        between the existing mask vent (which by this point has been reoriented, resized and warped),
        and the current split (e.g. the right-middle lobe).
        
        The "product" image is not deleted and can be inspected.
        
        The same procedure shown below to produce a "product" should be repeated 
        for all the images involved in computing the defect percentages
        for RBC and membrane
        
        Check the following images in ITK-SNAP:
        1. image_gas_binned
        2. image_rbc2gas_binned
        3. image_rbc2gas
        4. image_membrane2gas_binned 
        5. image_membrane2gas
        6. mask_vent (mask_reg_edited with defect regions removed, resized, reoriented and warped)
        7. mask (mask_reg_edited, resized, reoriented and warped)
        
        All these images should:
        - Have the same shape as CT_mask 
        
        For each of the first five images, we should take its product 
        with the current split in this for loop and 
        reset the relevant.
        
        Since get_statistics uses all five images 
        and therefore computes bin percentages for ventilation, rbc and mem
        in one call, we have to compute five additonal products
        """

        """
        Haad:
        
        It turns that when we compute the split product,
        the pixel intensities in the split resulting from the original image
        are multiplied by the pixel intensity of that split.
        
        For example, if the binned image is rbc2gas_binned and 
        the pixel intesities in the bins are 1, 2, and 3,
        and our current split is the left-upper lobe, which has a pixel
        intensity of 8, then the pixel intensities of the bins in the 
        resulting product image will be 8, 16, and 24.
        
        So one solution is to divide the resulting product image
        by the pixel intensity of the current split. This can be 
        done right after retrieving the underlying float data 
        of the product image (after the call to compute_split_product).
        
        """

        # Computing intersection between split and processed mask_vent
        mask_vent_path = os.path.join(
            subject.config.data_dir, "mask_vent_mutated_affine_resized_warped.nii"
        )
        subject.mask_vent = nib.load(
            compute_split_product(mask_vent_path, split)
        ).get_fdata()

        # Dividing the data of the product by the currrent pixel intensity
        subject.mask_vent = subject.mask_vent / 8
        print(
            f"stats.py: Set subject.mask_vent to its intersection with the current split ({split})"
        )

        # Computing intersection between split and processed image_gas_binned
        image_gas_binned_path = os.path.join(
            subject.config.data_dir,
            "image_gas_binned_mutated_affine_resized_warped.nii",
        )
        subject.image_gas_binned = nib.load(
            compute_split_product(image_gas_binned_path, split)
        ).get_fdata()
        print(
            f"stats.py: Set subject.image_gas_binned to its intersection with the current split ({split})"
        )

        # Computing intersection between split and processed image_rbc2gas_binned
        image_rbc2gas_binned_path = os.path.join(
            subject.config.data_dir,
            "image_rbc2gas_binned_mutated_affine_resized_warped.nii",
        )
        subject.image_rbc2gas_binned = nib.load(
            compute_split_product(image_rbc2gas_binned_path, split)
        ).get_fdata()
        print(
            f"stats.py: Set subject.image_rbc2gas_binned to its intersection with the current split ({split})"
        )

        # Computing intersection between split and processed image_rbc2gas
        image_rbc2gas_path = os.path.join(
            subject.config.data_dir, "image_rbc2gas_mutated_affine_resized_warped.nii"
        )
        subject.image_rbc2gas = nib.load(
            compute_split_product(image_rbc2gas_path, split)
        ).get_fdata()
        print(
            f"stats.py: Set subject.image_rbc2gas to its intersection with the current split ({split})"
        )

        # Computing intersection between split and processed image_membrane2gas_binned
        image_membrane2gas_binned_path = os.path.join(
            subject.config.data_dir,
            "image_membrane2gas_binned_mutated_affine_resized_warped.nii",
        )
        subject.image_membrane2gas_binned = nib.load(
            compute_split_product(image_membrane2gas_binned_path, split)
        ).get_fdata()
        print(
            f"stats.py: Set subject.image_membrane2gas_binned to its intersection with the current split ({split})"
        )

        # Computing intersection between split and processed image_membrane2gas
        image_membrane2gas_path = os.path.join(
            subject.config.data_dir,
            "image_membrane2gas_mutated_affine_resized_warped.nii",
        )
        subject.image_membrane2gas = nib.load(
            compute_split_product(image_membrane2gas_path, split)
        ).get_fdata()
        print(
            f"stats.py: Set subject.image_membrane2gas to its intersection with the current split ({split})"
        )

        # Retreiving dictionary to get values like fov
        with open(f"{subject.config.data_dir}/dict_dis.pkl", "rb") as f:
            dict_dis = pickle.load(f)  # deserialize using load()
            # print(dict_dis)

        subject.dict_dis = dict_dis
        subject.get_statistics()
        subject.write_stats_to_csv()

        '''
         input(f"""
              stats.py:
              \n\tFinished computing ventilation, RBC and membrane defect percentages and means for patient {subject.config.subject_id}.
              \n\tPlease view the following images in ITK-SNAP:
              \n\t\timage_gas_binned.nii
              \n\t\timage_rbc2gas.nii
              \n\t\timage_rbc2gas_binned.nii
              \n\t\timage_membrane2gas.nii
              \n\t\timage_membrane2gas_binned.nii
              \n\t\tmask_reg_edited_mutated_affine_resized_warped.nii
              \n\t\tmask_vent_mutated_affine_resized_warped.nii
              \n\tPress enter to continue once you have viewed these images. 
              """)

        '''
        # os.remove(new_vent)

    """
    Haad: 
    Outside the for loop, editt the final csv file to remove the first column
    which contains the rbc_m_ratio in the config (which should be 0 because we 
    manually specify it).
    
    Replace this column with the names of the regions/splits (e.g. core, peel, 
    RUL, etc.).
    """


def main(argv):
    """Run the gas exchange imaging pipeline.

    Either run the reconstruction or read in the .mat file.
    """
    config = _CONFIG.value
    config.data_dir = FLAGS.patient_path
    config.subject_id = os.path.basename(config.data_dir)
    # Set data dir from flag argument
    if not os.path.isfile(
        f"{config.data_dir}/{os.path.basename(config.data_dir)}_stats.csv"
    ):
        compute_patient_stats(config)
    else:
        print(
            f"Stats already computed for patient: {os.path.basename(config.data_dir)}"
        )


if __name__ == "__main__":
    app.run(main)
