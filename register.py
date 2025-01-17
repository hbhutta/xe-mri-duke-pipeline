import os
import ants
import pickle
from multiprocessing import Pool
from utils.os_utils import get_subdirs

from datetime import datetime

BASE_DIR = "cohort"

patient_paths = get_subdirs(dir_=BASE_DIR) # ['cohort/PIm0015', 'cohort/PIm0018', 'cohort/PIm0019', 'cohort/PIm0020', 'cohort/PIm0023', 'cohort/PIm0025', 'cohort/PIm0028', 'cohort/PIm0029', 'cohort/PIm0031', 'cohort/PIm0032']

ct_mask_file_paths = [os.path.join(patient, "CT_mask_neg_affine.nii") for patient in patient_paths]
mri_file_paths = [os.path.join(patient, "mask_reg_edited_mutated_affine.nii") for patient in patient_paths]

assert len(ct_mask_file_paths) == len(patient_paths)
assert len(mri_file_paths) == len(patient_paths)

print(patient_paths)
print(ct_mask_file_paths)
print(mri_file_paths)

def register(ct_filename: str, mri_filename: str, save_dir: str) -> None:
    if (not os.path.isfile(f"{save_dir}/{os.path.basename(save_dir)}_reg.pkl")):
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

        print(f"Finished similarity registration for patient {os.path.basename(save_dir)}!\n\n\n")

        with open(f"{save_dir}/{os.path.basename(save_dir)}_reg.pkl", "wb") as file:
            pickle.dump(reg, file)
            print(f"{save_dir}/{os.path.basename(save_dir)}_reg.pkl saved!")
    else:
        print(f"Registration already done for {os.path.basename(save_dir)}, skipping...")

#def main():
#    for ct_mask, mri, subdir in zip(ct_mask_file_paths, mri_file_paths, patient_paths):
#        print(f"register.py: Registering CT mask to MRI for patient {os.path.basename(subdir)}")
#        register(ct_filename=ct_mask, mri_filename=mri, save_dir=subdir)

def main():
    with Pool() as pool:
        pool.starmap(register, zip(ct_mask_file_paths, mri_file_paths, patient_paths))

if __name__ == '__main__':
    start = datetime.now()
    main()
    end = datetime.now()
    elapsed = (end - start).seconds / 60
    print(f"That took {elapsed} minutes")