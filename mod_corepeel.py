"""
Author: Haad Bhutta
Updated: July 31, 2025


"""

import os
import nibabel as nib

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


def mod_corepeel_mask(patient_path: str) -> None:
    ct_mask_path = os.path.join(patient_path, "CT_mask_neg_affine.nii")
    ct_mask = nib.load(ct_mask_path)
    q, px, py, pz = ct_mask.header["pixdim"][0:4]
    qoffset_x = ct_mask.header["qoffset_x"]
    qoffset_y = ct_mask.header["qoffset_y"]
    qoffset_z = ct_mask.header["qoffset_z"]

    # Modify origin (qoffsets) and pixdims (voxel size)
    os.system(
        f"nifti_tool -mod_hdr -mod_field pixdim '{q} {px} {py} {pz} 0.0 0.0 0.0 0.0' -prefix {patient_path}/ct_corepeel_mask_neg_affine_mod.nii -infiles {patient_path}/ct_corepeel_mask_neg_affine.nii"
    )
    os.system(
        f"nifti_tool -mod_hdr -mod_field qoffset_x {qoffset_x} -prefix {patient_path}/ct_corepeel_mask_neg_affine_mod_x.nii -infiles {patient_path}/ct_corepeel_mask_neg_affine_mod.nii"
    )
    os.system(
        f"nifti_tool -mod_hdr -mod_field qoffset_y {qoffset_y} -prefix {patient_path}/ct_corepeel_mask_neg_affine_mod_x_y.nii -infiles {patient_path}/ct_corepeel_mask_neg_affine_mod_x.nii"
    )
    os.system(
        f"nifti_tool -mod_hdr -mod_field qoffset_z {qoffset_z} -prefix {patient_path}/ct_corepeel_mask_neg_affine_mod_x_y_z.nii -infiles {patient_path}/ct_corepeel_mask_neg_affine_mod_x_y.nii"
    )

    # Delete intermediate files
    os.remove(f"{patient_path}/ct_corepeel_mask_neg_affine_mod.nii")
    os.remove(f"{patient_path}/ct_corepeel_mask_neg_affine_mod_x.nii")
    os.remove(f"{patient_path}/ct_corepeel_mask_neg_affine_mod_x_y.nii")


def main(argv):
    config = _CONFIG.value
    config.data_dir = FLAGS.patient_path
    patient_path = config.data_dir
    
    print("mod_corepeel.py: patient path:", patient_path)
    
    mod_corepeel_mask(patient_path=patient_path)


if __name__ == "__main__":
    # input("Running mod_corepeel.py. Press Enter to continue...")
    app.run(main)
