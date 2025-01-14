try:
    from utils.os_utils import get_subdirs
except ImportError as e:
    print(f"An error occurred: {e}")

import os
import ants
from sys import argv
import pickle
from time import time
from utils.os_utils import get_common_files

start_time = time()
BASE_DIR = argv[1]


# Make sure to use scaled/trasnformed files instead of original
# ct_mask_file_paths = get_common_files(
#     base_dir=BASE_DIR, filename='CT_mask_neg_affine.nii')[0:1]

# mri_file_paths = get_common_files(
#     base_dir=BASE_DIR, filename='mask_reg_edited_scaled_mutated_affine.nii')[0:1]

# ventilation_file_paths = get_common_files(
#     base_dir=BASE_DIR, filename='gas_highreso_scaled_mutated_affine.nii')[0:1]

# testing with pim0072
ct_mask_file_paths = ["imgs/PIm0072/CT_mask_neg_affine.nii"]
mri_file_paths = ["imgs/PIm0072/mask_reg_edited_scaled_mutated_affine.nii"]
ventilation_file_paths = ["imgs/PIm0072/gas_highreso_scaled_mutated_affine.nii"]
subdir_paths = ["imgs/PIm0072"]

#subdir_paths = get_subdirs(dir=BASE_DIR)[0:1]

#print(ct_mask_file_paths)
#print(mri_file_paths)
#print(ventilation_file_paths)
#print(subdir_paths)

def register(ct_filename: str, mri_filename: str, patient: str) -> None:
    ct_ants = ants.image_read(filename=ct_filename)
    mri_ants = ants.image_read(filename=mri_filename)

    type_of_transform = "Similarity"
    prep = ants.registration(
        fixed=ct_ants, moving=mri_ants, type_of_transform=type_of_transform, verbose=True)

    transform_file = prep['fwdtransforms'][0]
    print('Using initial transformation file: {}'.format(transform_file))

    reg = ants.registration(fixed=ct_ants,
                            moving=mri_ants,
                            type_of_transform='SyNAggro',  # deformation
                            initial_transform=transform_file,
                            outprefix='',
                            mask=None,
                            moving_mask=None,
                            grad_step=0.2,
                            flow_sigma=3,
                            total_sigma=0,
                            aff_metric="mattes",
                            aff_sampling=16,
                            aff_random_sampling_rate=0.2,
                            syn_metric="mattes",
                            syn_sampling=16,
                            reg_iterations=(40, 20, 0),
                            aff_iterations=(2100, 1200, 1200, 10),
                            aff_shrink_factors=(6, 4, 2, 1),
                            aff_smoothing_sigmas=(3, 2, 1, 0),
                            write_composite_transform=False,
                            random_seed=1,  # set to 1 for reproducibility
                            verbose=True,
                            multivariate_extras=None)

    print(f"Finished similarity registration for patient {
          os.path.basename(patient)}!\n\n\n")

    with open(f"{patient}/{os.path.basename(patient)}_reg.pkl", "wb") as file:
        pickle.dump(reg, file)
        print(f"{patient}/{os.path.basename(patient)}_reg.pkl saved!")


for ct_mask, mri, vent, subdir in zip(ct_mask_file_paths, mri_file_paths, ventilation_file_paths, subdir_paths):
    print(f"register.py: Registering CT mask to MRI for patient {os.path.basename(subdir)}")
    print(f"ct {ct_mask} | mri {mri} | vent {
          vent} | patient {os.path.basename(subdir)}")
    register(ct_filename=ct_mask, mri_filename=mri, patient=subdir)
end_time = time()
print(f"That took: {end_time - start_time} mins/seconds")
