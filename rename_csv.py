"""Scripts to run gas exchange mapping pipeline."""

# Libraries
from absl import app, flags
from ml_collections import config_flags
import pandas as pd
import os
import glob

FLAGS = flags.FLAGS

_CONFIG = config_flags.DEFINE_config_file("config", None, "config file.")

flags.DEFINE_string(
    name="patient_path",
    default=None,  # assuming that this is where .dat files are stored by default
    help="The folder where the .dat files are stored",
    required=True,
)

flags.DEFINE_boolean(
    name="sublobe", default=False, help="Include sub-lobe names in renamed CSV file"
)

# Adapted from: https://github.com/TeamXenonDuke/xenon-bronchoscopy/blob/main/generate_report.py#L45
sublobe_lookup = [None] * 255
sublobe_lookup[1] = "LB1"
sublobe_lookup[2] = "LB2"
sublobe_lookup[3] = "LB3"
sublobe_lookup[4] = "LB4"
sublobe_lookup[5] = "LB5"
sublobe_lookup[6] = "LB1_2"
sublobe_lookup[7] = "LB4_5"
sublobe_lookup[102] = "LB6"
sublobe_lookup[104] = "LB8"
sublobe_lookup[105] = "LB9"
sublobe_lookup[106] = "LB10"
sublobe_lookup[129] = "RB1"
sublobe_lookup[130] = "RB2"
sublobe_lookup[131] = "RB3"
sublobe_lookup[164] = "RB4"
sublobe_lookup[165] = "RB5"
sublobe_lookup[230] = "RB6"
sublobe_lookup[231] = "RB7"
sublobe_lookup[232] = "RB8"
sublobe_lookup[233] = "RB9"
sublobe_lookup[234] = "RB10"
# sublobe_lookup[8] = "ucLUL"
# sublobe_lookup[16] = "ucLLL"
# sublobe_lookup[32] = "ucRUL"
# sublobe_lookup[64] = "ucRML"
# sublobe_lookup[128] = "ucRLL"


def get_split_names(patient_path: str) -> list:
    split_paths = glob.glob(
        f"{FLAGS.patient_path}/CT_sublobe_mask_neg_affine_split_*.nii"
    )
    detected_split_intensities = [
        int(os.path.basename(split).split("_")[-1].replace(".nii", ""))
        for split in split_paths
    ]

    detected_split_names = [
        sublobe_lookup[intensity]
        for intensity in detected_split_intensities
        if intensity < len(sublobe_lookup) and sublobe_lookup[intensity] is not None
    ]

    return detected_split_names


def main(argv):
    """Run the gas exchange imaging pipeline.

    Either run the reconstruction or read in the .mat file.
    """
    config = _CONFIG.value
    config.data_dir = FLAGS.patient_path
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
            "LUL",
            "LLL",
            "RUL",
            "RML",
            "RLL",
            "Core",
            "Peel",
            "Whole",
        ]

        if FLAGS.sublobe:
            sublobe_split_names = get_split_names(config.data_dir)
            region_names += sublobe_split_names

        df["rbc_m_ratio"] = region_names
        df.rename(columns={"rbc_m_ratio": "region"}, inplace=True)
        df.to_csv(stats_file_path, index=False)


if __name__ == "__main__":
    app.run(main)

    # print("Including sub-lobe names in the renamed CSV file.")
    # region_names += [
    #     "LB1_2",  # Left upper lobe: LB1/2 and LB3
    #     "LB3",
    #     "LB4",  # Lingula: LB4 and LB5
    #     "LB5",
    #     "LB6",  # Left lower lobe: LB 6,8,9,10
    #     "LB8",
    #     "LB9",
    #     "LB10",
    #     "RB1",  # Right upper lobe: RB 1,2,3
    #     "RB2",
    #     "RB3",
    #     "RB4",  # Right middle lobe: RB4 and RB5
    #     "RB5",
    #     "RB6",  # Right lower lobe: RB 6,7,8,9,10
    #     "RB7",
    #     "RB8",
    #     "RB9",
    #     "RB10",
    # ]
