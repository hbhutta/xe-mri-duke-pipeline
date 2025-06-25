from utils.os_utils import get_subdirs, get_common_files
import os
from glob import glob
import nibabel as nib
from sys import argv
import pickle
import ants

patient_paths = [argv[1]]
print(patient_paths)

def check_match(ants_ct, warped_proton):
    try:
        # Check shape
        if ants_ct.shape != warped_proton.shape:
            raise AssertionError(f"Shape mismatch: ants_ct.shape={ants_ct.shape}, warped_proton.shape={warped_proton.shape}")

        # Check dimensions
        if ants_ct.dimension != warped_proton.dimension:
            raise AssertionError(f"Dimension mismatch: ants_ct.dimension={ants_ct.dimension}, warped_proton.dimension={warped_proton.dimension}")

        # Check spacing
        if ants_ct.spacing != warped_proton.spacing:
            raise AssertionError(f"Spacing mismatch: ants_ct.spacing={ants_ct.spacing}, warped_proton.spacing={warped_proton.spacing}")

        # Check origin
        if ants_ct.origin != warped_proton.origin:
            raise AssertionError(f"Origin mismatch: ants_ct.origin={ants_ct.origin}, warped_proton.origin={warped_proton.origin}")

    except AssertionError as e:
        print(f"Assertion failed: {e}")

ct_mask_file_paths = [os.path.join(patient, "CT_mask_neg_affine.nii") for patient in patient_paths]

for ct_mask_file, patient in zip(ct_mask_file_paths, patient_paths):
    print(f"unpack.py: Processing patient {patient}")
    pim = os.path.basename(patient)
    pkls = glob(f"{patient}/{pim}_*.pkl")
    
    for pkl in pkls:
        with open(pkl, "rb") as file:
            reg = pickle.load(file)

        warped_proton = reg['warpedmovout']

        if "reg" in pkl:
            dst = f"{patient}/mask_reg_edited_mutated_affine_resized_warped.nii" # should dst have a .gz extension
        elif "vent" in pkl:
            dst = f"{patient}/mask_vent_mutated_affine_resized_warped.nii" # should dst have a .gz extension

        ants_ct = ants.image_read(ct_mask_file)
        check_match(ants_ct, warped_proton)
        ants.image_write(image=warped_proton, filename=dst)
        print(f"Wrote ANTsImage to: {dst}")
    #print(ants.read_transform(reg['fwdtransforms'][1]).parameters)
