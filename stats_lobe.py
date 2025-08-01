"""Scripts to run gas exchange mapping pipeline."""

# Libraries
from absl import app, flags
from ml_collections import config_flags
import os
# import numpy as np
# import pandas as pd

# Utils
from utils.stats_utils import compute_patient_stats
from utils.img_utils import homogenize_mask

FLAGS = flags.FLAGS

_CONFIG = config_flags.DEFINE_config_file("config", None, "config file.")

flags.DEFINE_string(
    name="patient_path",
    default=None,  # assuming that this is where .dat files are stored by default
    help="The folder where the .dat files are stored",
    required=True,
)

flags.DEFINE_boolean(
    name="sublobe", default=False, help="Whether or not to compute sub-lobe stats"
)

def main(argv):
    """Run the gas exchange imaging pipeline.

    Either run the reconstruction or read in the .mat file.
    """
    config = _CONFIG.value
    config.data_dir = FLAGS.patient_path
    config.subject_id = os.path.basename(FLAGS.patient_path)
    patient_id = config.subject_id
    
    print("PATIENT PATH:", FLAGS.patient_path)
    
    stats_file_path = f"{FLAGS.patient_path}/{patient_id}_stats.csv"
    
    if not os.path.isfile(stats_file_path):
        print(os.path.join(FLAGS.patient_path, "CT_mask_neg_affine.nii"))
        homogenize_mask(mask_path=os.path.join(FLAGS.patient_path, "CT_mask_neg_affine.nii"))
        masks = [
            os.path.join(FLAGS.patient_path, mask)
            for mask in [
                "CT_lobe_mask_neg_affine.nii",  # Splits into the five lobes
                "ct_corepeel_mask_neg_affine_mod_x_y_z.nii",  # Splits into the core and peel
                "CT_mask_neg_affine_homogenized.nii",  # Whole lung mask
            ]
        ]

        if FLAGS.sublobe:
            masks.append(
                os.path.join(FLAGS.patient_path, "CT_sublobe_mask_neg_affine.nii")
            )
            print("Computing sub-lobe stats as well")
        else:
            print("Skipping sub-lobe stats computation")

        compute_patient_stats(config=config, masks=masks)

if __name__ == "__main__":
    app.run(main)
