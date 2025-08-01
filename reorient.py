# from utils.os_utils import aff2axcodes_RAS
import os
import nibabel as nib
import numpy as np

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

# if len(sys.argv) < 2:
#     print("Usage: python reorient.py <patient_dir>")
#     sys.exit(1)

# PATIENT_DIR = sys.argv[1]
# patient = PATIENT_DIR

# these cts will not be warped or resized, only reoriented
# ct_mask_paths = [
#     os.path.join(patient, "CT_mask.nii"),
#     os.path.join(patient, "CT_lobe_mask.nii"),
#     os.path.join(patient, "ct_corepeel_mask.nii"),
# ]

# if os.path.exists(os.path.join(patient, "CT_sublobe_mask.nii")):
#     print(f"Found CT sublobe mas for patient {patient}. Will reorient it.")
#     ct_mask_paths.append(os.path.join(patient, "CT_sublobe_mask.nii"))
# else:
#     print("No sublobe mask found for patient {patient}.")

# # Skip reorienting CTs if they are already reoriented
# are_cts_reoriented = True
# for ct in ct_mask_paths:
#     if not os.path.isfile(ct[:-4] + "_neg_affine.nii"):
#         are_cts_reoriented = False
#         print(f"File {ct} does not exist. Will redo reorientation of CT masks.")
#         break

# """
# Reorient CT mask (CT_mask.nii) 
# """
# if not are_cts_reoriented:
#     for ct_mask_file in ct_mask_paths:
#         print(
#             f"reorient.py: Reorienting patient {os.path.dirname(ct_mask_file)} CT mask"
#         )
#         # print(ct_mask_file)

#         nib_ct = nib.load(ct_mask_file)

#         aff = nib_ct.affine
#         for i in range(3):
#             if aff[i][i] > 0:
#                 aff[i][i] = -aff[i][i]

#         nib_ct.set_qform(aff)
#         path = ct_mask_file[:-4] + "_neg_affine.nii"
#         if not os.path.exists(path):
#             nib.save(img=nib_ct, filename=path)
#             # print(f"Saved to {path}!")
#             # print(aff2axcodes_RAS(nib_ct.affine))

#         else:
#             print(f"File {path} already exists.")

# mri_type_image_paths = [
#     os.path.join(patient, "mask_reg_edited.nii"),
#     os.path.join(patient, "image_gas_highreso.nii"),
#     os.path.join(patient, "image_gas_binned.nii"),
#     os.path.join(patient, "image_gas_cor.nii"),
#     os.path.join(patient, "image_rbc2gas_binned.nii"),
#     os.path.join(patient, "image_rbc2gas.nii"),
#     os.path.join(patient, "mask_vent.nii"),
#     os.path.join(patient, "image_membrane.nii"),
#     os.path.join(patient, "image_membrane2gas_binned.nii"),
#     os.path.join(patient, "image_membrane2gas.nii"),
#     os.path.join(patient, "image_gas_binned.nii"),
# ]

# are_mri_reoriented = True
# for mri in mri_type_image_paths:
#     if not os.path.isfile(mri[:-4] + "_mutated_affine.nii"):
#         are_mri_reoriented = False
#         print(
#             f"File {mri} does not exist. Will redo MRI reorientation MRI type images."
#         )
#         break


# """
# Reorient MRI (mask_reg_edited_scaled.nii) and ventilation (gas_highreso_scaled.nii)
# """
# if not are_mri_reoriented:
#     for mri_file in mri_type_image_paths:
#         print(
#             f"reorient.py: Reorienting patient {os.path.dirname(mri_file)} ventilation and MRI"
#         )

#         # print(mri_file)
#         nib_mr = nib.load(mri_file)
#         new_aff = np.array([[0, -1, 0, 0], [0, 0, -1, 0], [-1, 0, 0, 0], [0, 0, 0, 1]])
#         nib_mr.set_qform(new_aff)
#         mr_path = mri_file[:-4] + "_mutated_affine.nii"

#         # MRI
#         if not os.path.exists(mr_path):
#             nib.save(img=nib_mr, filename=mr_path)
#             # print(f"Saved to {mr_path}!")
#             # print(aff2axcodes_RAS(nib_mr.affine))
#         else:
#             print(f"File {mr_path} already exists.")


def reorient_mri(patient_path: str) -> None:
    """Reorient MRI-type images in the specified patient directory."""
    mri_names = [
        "mask_reg_edited.nii",
        "image_gas_highreso.nii",
        "image_gas_binned.nii",
        "image_gas_cor.nii",
        "image_rbc2gas_binned.nii",
        "image_rbc2gas.nii",
        "mask_vent.nii",
        "image_membrane.nii",
        "image_membrane2gas_binned.nii",
        "image_membrane2gas.nii",
        "image_gas_binned.nii",
    ]
    mri_paths = [os.path.join(patient_path, name) for name in mri_names]

    for mri_mask_path in mri_paths:
        reoriented_mask_path = mri_mask_path[:-4] + "_mutated_affine.nii"
        if os.path.exists(reoriented_mask_path):
            print(f"reorient.py: File {reoriented_mask_path} already exists. Skippping")
            continue

        nib_mr = nib.load(mri_mask_path)
        new_aff = np.array([[0, -1, 0, 0], [0, 0, -1, 0], [-1, 0, 0, 0], [0, 0, 0, 1]])

        nib_mr.set_qform(new_aff)
        nib.save(img=nib_mr, filename=reoriented_mask_path)

def reorient_ct(patient_path: str) -> None:
    """Reorient CT images in the specified patient directory."""
    ct_mask_names = ["CT_mask.nii", "CT_lobe_mask.nii", "ct_corepeel_mask.nii"]
    ct_mask_paths = [os.path.join(patient_path, name) for name in ct_mask_names]

    if os.path.exists(os.path.join(patient_path, "CT_sublobe_mask.nii")):
        print(
            f"reorient.py: Found CT sublobe mask for patient {patient_path}. Will reorient it."
        )
        ct_mask_paths.append(os.path.join(patient_path, "CT_sublobe_mask.nii"))
    else:
        print(f"reorient.py: No sublobe mask found for patient {patient_path}.")

    for ct_mask_path in ct_mask_paths:
        reoriented_mask_path = ct_mask_path[:-4] + "_neg_affine.nii"
        if os.path.exists(reoriented_mask_path):
            print(f"reorient.py: File {reoriented_mask_path} already exists. Skippping")
            continue

        nib_ct = nib.load(ct_mask_path)
        aff = nib_ct.affine
        for i in range(3):
            if aff[i][i] > 0:
                aff[i][i] = -aff[i][i]

        nib_ct.set_qform(aff)
        nib.save(img=nib_ct, filename=reoriented_mask_path)


def main(argv):
    config = _CONFIG.value
    config.data_dir = FLAGS.patient_path
    patient_path = config.data_dir
   
    print("reorient.py: Patient_path:", patient_path)
    
    reorient_ct(patient_path=patient_path)
    reorient_mri(patient_path=patient_path)

if __name__ == "__main__":
    # input("Running reorient.py. Press Enter to continue...")
    app.run(main)
