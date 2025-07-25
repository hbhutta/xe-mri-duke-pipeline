"""
Helper functions used in stats_lobes.py and stats_sublobes.py scripts.
"""

# Libraries
import nibabel as nib
import numpy as np
import pickle as pkl
import os

# Classes
from config import base_config
from subject_classmap import Subject

# Utils
from utils.img_utils import split_mask, homogenize_mask
from utils.os_utils import basename


def compute_split_product(img_path: str, split_path: str) -> str:
    """
    Given the path to an image (img_path) and the path to a split (split_path),
    compute the product of the two images and save it as a new NIFTI file.
    """
    if not os.path.isfile(img_path):
        raise FileNotFoundError(f"File {img_path} does not exist")
    new_img_path = os.path.join(
        os.path.dirname(img_path),
        f"{basename(img_path)}__{basename(split_path)}_product.nii",
    )
    cmd = f"./bin/c3d -verbose {img_path} {split_path} -multiply -o {new_img_path}"
    os.system(cmd)
    return new_img_path


def get_intensity_from_split(split_path: str) -> float:
    """
    Given the path to a split mask, return the intensity of the split
    based on the suffix of the path.

    Assumes that the split path is of the form:
    <split_name>_<intensity>.nii
    """
    if not os.path.isfile(split_path):
        raise FileNotFoundError("File {split_path} does not exist")
    filename_without_ext = basename(split_path)
    intensity = float(filename_without_ext.split("_")[-1])
    return intensity


def compute_patient_stats(config: base_config.Config, masks: list) -> None:
    subject = Subject(config=config)

    splits_by_mask = [split_mask(mask) for mask in masks]

    # splits_by_mask is a list of lists, each list being the splits for a single mask, so we need to flatten it
    split_paths = []
    for splits_list in splits_by_mask:
        for split in splits_list:
            split_paths.append(split)

    # Append homogenized CT whole lung mask to split_paths separately
    # so it doesn't get split into 20 and 30
    homogenize_mask(mask_path=os.path.join(config.data_dir, "CT_mask_neg_affine.nii"))
    split_paths.append(
        os.path.join(config.data_dir, "CT_mask_neg_affine_homogenized_PI_1.nii")
    )

    # Enumerate the images that will be used in computing the bin percentages
    image_names = [
        "image_gas_highreso",
        "image_gas_binned",
        "image_gas_cor",
        "image_rbc2gas_binned",
        "image_rbc2gas",
        "image_membrane",
        "image_membrane2gas_binned",
        "image_membrane2gas",
        "image_gas_binned",
    ]
    image_paths = [
        os.path.join(
            subject.config.data_dir, f"{image}_mutated_affine_resized_warped.nii"
        )
        for image in image_names
    ]

    # For each image, load the NIFTI file and set the corresponding attribute in the subject
    for image_name, image_path in zip(image_names, image_paths):
        image_nib = nib.load(image_path)
        image_data = image_nib.get_fdata()
        setattr(subject, basename(image_name), image_data)

    # Enumerate the split product targets that will be used in computing the bin percentages
    target_names = [
        "mask_vent",  # mask_vent (MRI mask without ventilation defects)
        "image_gas_binned",
        "image_rbc2gas_binned",
        "image_rbc2gas",
        "image_membrane2gas_binned",
        "image_membrane2gas",
    ]
    target_paths = [
        os.path.join(
            subject.config.data_dir, f"{target}_mutated_affine_resized_warped.nii"
        )
        for target in target_names
    ]

    for split_path in split_paths:
        # Set the current split mask
        setattr(subject, "mask", np.where(nib.load(split_path).get_fdata() > 0.5, 1, 0))

        # Compute the split product for each target and set the corresponding attribute in the subject
        # These attributes of the current subject are re-set for every split
        for target_name, target_path in zip(target_names, target_paths):
            split_product = compute_split_product(target_path, split_path)
            split_product_nib = nib.load(split_product).get_fdata()
            if ("binned" in target_name) or target_name == "mask_vent":
                setattr(
                    subject,
                    target_name,
                    split_product_nib / get_intensity_from_split(split_path=split_path),
                )
            else:
                setattr(subject, basename(target_path), split_product_nib)

        # This is at the correct level of indentation to ensure get_statistics() is called for each split
        # Retreiving dictionary to get values like fov
        with open(f"{subject.config.data_dir}/dict_dis.pkl", "rb") as f:
            dict_dis = pkl.load(f)
        subject.dict_dis = dict_dis

        subject.get_statistics()
        subject.write_stats_to_csv()

   
