"""Scripts to run gas exchange mapping pipeline."""
import logging
import pickle 
import nibabel as nib
import numpy as np

from utils.img_utils import split_mask

import dask.array as da

from absl import app, flags
from ml_collections import config_flags

from config import base_config
from subject_classmap import Subject

import os

FLAGS = flags.FLAGS

_CONFIG = config_flags.DEFINE_config_file("config", None, "config file.")

def make_bool(data: np.ndarray):
    process = np.where(np.abs(data-1) < np.abs(data-0), 1, 0) 
    return process

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
    imgs = [
            "mask_reg_edited.nii",
            "image_gas_highreso.nii"
            "image_gas_binned.nii",
            "image_gas_cor.nii",
            "image_rbc2gas_binned.nii",
            "image_rbc2gas.nii",
            "mask_vent.nii",
            "image_membrane.nii",
            "image_membrane2gas_binned.nii",
            "image_membrane2gas.nii",
            "image_gas_binned.nii"
            ]

    masks = ["CT_lobe_mask.nii", "ct_corepeel_mask.nii"]
    masks = [os.path.join(f"{subject.config.data_dir}", mask) for mask in
            masks]
   
    splits = []
    for mask in masks:
        splits += split_mask(mask)

    for split in splits:
        print(f"Processing split {split}")
        subject.mask = np.where(nib.load(split).get_fdata() > 0.5, 1, 0)
        subject.image_gas_highreso = nib.load(os.path.join(subject.config.data_dir,"image_gas_highreso_mutated_affine_resized_warped.nii")).get_fdata()
        subject.image_gas_binned = nib.load(os.path.join(subject.config.data_dir, "image_gas_binned_mutated_affine_resized_warped.nii")).get_fdata()
        subject.image_gas_cor = nib.load(os.path.join(subject.config.data_dir, "image_gas_cor_mutated_affine_resized_warped.nii")).get_fdata()
        subject.image_rbc2gas_binned = nib.load(os.path.join(subject.config.data_dir, "image_rbc2gas_binned_mutated_affine_resized_warped.nii")).get_fdata()
        subject.image_rbc2gas = nib.load(os.path.join(subject.config.data_dir, "image_rbc2gas_mutated_affine_resized_warped.nii")).get_fdata()
        subject.image_membrane = nib.load(os.path.join(subject.config.data_dir, "image_membrane_mutated_affine_resized_warped.nii")).get_fdata()
        subject.image_membrane2gas_binned = nib.load(os.path.join(subject.config.data_dir, "image_membrane2gas_binned_mutated_affine_resized_warped.nii")).get_fdata()
        subject.image_membrane2gas = nib.load(os.path.join(subject.config.data_dir, "image_membrane2gas_mutated_affine_resized_warped.nii")).get_fdata()
        subject.image_gas_binned = nib.load(os.path.join(subject.config.data_dir, "image_gas_binned_mutated_affine_resized_warped.nii")).get_fdata()

        subject.mask_vent = nib.load(os.path.join(subject.config.data_dir, "mask_vent_mutated_affine_resized_warped.nii")).get_fdata()


        # Retreiving dictionary to get values like fov
        with open(f'{subject.config.data_dir}/dict_dis.pkl', 'rb') as f:
            dict_dis = pickle.load(f) # deserialize using load()
            # print(dict_dis) # print student names
            subject.dict_dis = dict_dis
        subject.get_statistics()
        subject.write_stats_to_csv()

def main(argv):
    """Run the gas exchange imaging pipeline.

    Either run the reconstruction or read in the .mat file.
    """
    config = _CONFIG.value

    # Set data dir from flag argument
    compute_patient_stats(config)

if __name__ == "__main__":
    app.run(main)


