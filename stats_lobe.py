"""Scripts to run gas exchange mapping pipeline."""

# Libraries
from absl import app, flags
from ml_collections import config_flags
import os

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


def main(argv):
    """Run the gas exchange imaging pipeline.

    Either run the reconstruction or read in the .mat file.
    """
    config = _CONFIG.value
    config.data_dir = FLAGS.patient_path
    config.subject_id = os.path.basename(config.data_dir)
    if not os.path.isfile(
        f"{config.data_dir}/{os.path.basename(config.data_dir)}_stats.csv"
    ):
        homogenize_mask(
            mask_path=os.path.join(config.data_dir, "CT_mask_neg_affine.nii")
        )
        masks = [
            os.path.join(config.data_dir, mask)
            for mask in [
                "CT_lobe_mask_neg_affine.nii", # Splits into the five lobes 
                "ct_corepeel_mask_neg_affine_mod_x_y_z.nii" # Splits into the core and peel
            ]
        ]
        print(masks)
        compute_patient_stats(config=config, masks=masks)
    else:
        print(
            f"Stats already computed for patient: {os.path.basename(config.data_dir)}"
        )


if __name__ == "__main__":
    app.run(main)
