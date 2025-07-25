"""Scripts to run gas exchange mapping pipeline."""

# Libraries
from absl import app, flags
# from ml_collections import config_flags
import pandas as pd
import os

FLAGS = flags.FLAGS

# _CONFIG = config_flags.DEFINE_config_file("", None, "config file.")

flags.DEFINE_string(
    name="patient_path",
    default=None,  # assuming that this is where .dat files are stored by default
    help="The folder where the .dat files are stored",
    required=True,
)

flags.DEFINE_boolean(
    name="sublobe", default=False, help="Include sub-lobe names in renamed CSV file"
)

def main(argv):
    """Run the gas exchange imaging pipeline.

    Either run the reconstruction or read in the .mat file.
    """
    # config = _CONFIG.value
    # config.data_dir = FLAGS.patient_path
    subject_id = os.path.basename(FLAGS.patient_path)
    stats_file_path = f"{FLAGS.patient_path}/{subject_id}_stats.csv"

    if not os.path.isfile(stats_file_path):
        raise FileNotFoundError(f"Stats file not found for patient: {subject_id}")
    else:
        print(f"Stats file found for patient: {subject_id} at {stats_file_path}")
    # Set the region names once all the stats have been computed
    df = pd.read_csv(stats_file_path)
    if "rbc_m_ratio" in df.columns:
        region_names = [
            "left_upper_lobe",
            "left_lower_lobe",
            "right_upper_lobe",
            "right_middle_lobe",
            "right_lower_lobe",
            "core",
            "peel",
            "whole_lung",
        ]

        if FLAGS.sublobe:
            print("Including sub-lobe names in the renamed CSV file.")
            region_names += [
                "LB1_2",  # Left upper lobe: LB1/2 and LB3
                "LB3",
                "LB4",  # Lingula: LB4 and LB5
                "LB5",
                "LB6",  # Left lower lobe: LB 6,8,9,10
                "LB8",
                "LB9",
                "LB10",
                "RB1",  # Right upper lobe: RB 1,2,3
                "RB2",
                "RB3",
                "RB4",  # Right middle lobe: RB4 and RB5
                "RB5",
                "RB6",  # Right lower lobe: RB 6,7,8,9,10
                "RB7",
                "RB8",
                "RB9",
                "RB10",
            ]
        df["rbc_m_ratio"] = region_names
        df.rename(columns={"rbc_m_ratio": "region"}, inplace=True)
        df.to_csv(stats_file_path, index=False)

if __name__ == "__main__":
    app.run(main)
