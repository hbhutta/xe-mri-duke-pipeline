import os
from glob import glob
import pickle
import ants

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


def check_match(ants_ct, warped_proton):
    try:
        # Check shape
        if ants_ct.shape != warped_proton.shape:
            raise AssertionError(
                f"Shape mismatch: ants_ct.shape={ants_ct.shape}, warped_proton.shape={warped_proton.shape}"
            )

        # Check dimensions
        if ants_ct.dimension != warped_proton.dimension:
            raise AssertionError(
                f"Dimension mismatch: ants_ct.dimension={ants_ct.dimension}, warped_proton.dimension={warped_proton.dimension}"
            )

        # Check spacing
        if ants_ct.spacing != warped_proton.spacing:
            raise AssertionError(
                f"Spacing mismatch: ants_ct.spacing={ants_ct.spacing}, warped_proton.spacing={warped_proton.spacing}"
            )

        # Check origin
        if ants_ct.origin != warped_proton.origin:
            raise AssertionError(
                f"Origin mismatch: ants_ct.origin={ants_ct.origin}, warped_proton.origin={warped_proton.origin}"
            )

    except AssertionError as e:
        print(f"Assertion failed: {e}")


def unpack_reg(patient_path: str) -> None:
    ct_mask_file_path = os.path.join(patient_path, "CT_mask_neg_affine.nii")

    print(f"unpack.py: Processing patient {patient_path}")
    pim = os.path.basename(patient_path)
    pkls = glob(f"{patient_path}/{pim}_*.pkl")

    for pkl in pkls:
        with open(pkl, "rb") as file:
            reg = pickle.load(file)

        warped_proton = reg["warpedmovout"]

        if "reg" in pkl:
            dst = f"{patient_path}/mask_reg_edited_mutated_affine_resized_warped.nii"  # should dst have a .gz extension
        elif "vent" in pkl:
            dst = f"{patient_path}/mask_vent_mutated_affine_resized_warped.nii"  # should dst have a .gz extension

        ants_ct = ants.image_read(ct_mask_file_path)
        check_match(ants_ct, warped_proton)
        ants.image_write(image=warped_proton, filename=dst)
        print(f"Wrote ANTsImage to: {dst}")
        # print(ants.read_transform(reg['fwdtransforms'][1]).parameters)


def main(argv):
    config = _CONFIG.value
    config.data_dir = FLAGS.patient_path
    patient_path = config.data_dir
    
    unpack_reg(patient_path=patient_path)

if __name__ == "__main__":
    # input("Running unpack.py. Press Enter to continue...")
    app.run(main)
