from utils.os_utils import get_subdirs, get_common_files
import os
import nibabel as nib
from sys import argv
import pickle
import ants

#BASE_DIR = argv[1]

patient_paths = ['cohort/PIm0015'] #, 'cohort/PIm0018', 'cohort/PIm0019', 'cohort/PIm0020', 'cohort/PIm0023', 'cohort/PIm0025', 'cohort/PIm0028', 'cohort/PIm0029', 'cohort/PIm0031', 'cohort/PIm0032']
ct_mask_file_paths = [os.path.join(patient, "CT_mask_neg_affine.nii") for patient in patient_paths]

for ct_mask_file, patient in zip(ct_mask_file_paths, patient_paths):
    print(f"unpack.py: Processing patient {patient}")
    with open(f"{patient}/{os.path.basename(patient)}_reg.pkl", "rb") as file:
        reg = pickle.load(file)
        print(reg)

        warped_proton = reg['warpedmovout']

        dst = f"{patient}/mask_reg_edited_mutated_affine_resized_warped.nii" # should dst have a .gz extension

        ants_ct = ants.image_read(ct_mask_file)

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
            break

    ants.image_write(image=warped_proton, filename=dst)
    print(f"Wrote ANTsImage to: {dst}")

    # Print and inspect the forward transforms from the registration
    print(ants.read_transform(reg['fwdtransforms'][1]).parameters)
