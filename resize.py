import nibabel as nib 
import os
import ants 

patients = [os.path.join("cohort/PIm0015")]

imgs = [
    [os.path.join(patient, "mask_reg_edited_mutated_affine.nii") for patient in patients],
    [os.path.join(patient, "image_gas_highreso_mutated_affine.nii") for patient in patients],
    [os.path.join(patient, "image_gas_binned_mutated_affine.nii") for patient in patients],
    [os.path.join(patient, "image_gas_cor_mutated_affine.nii") for patient in patients],
    [os.path.join(patient, "image_rbc2gas_binned_mutated_affine.nii") for patient in patients],
    [os.path.join(patient, "image_rbc2gas_mutated_affine.nii") for patient in patients],
    [os.path.join(patient, "mask_vent_mutated_affine.nii") for patient in patients],
    [os.path.join(patient, "image_membrane_mutated_affine.nii") for patient in patients],
    [os.path.join(patient, "image_membrane2gas_binned_mutated_affine.nii") for patient in patients],
    [os.path.join(patient, "image_membrane2gas_mutated_affine.nii") for patient in patients],
    [os.path.join(patient, "image_gas_binned_mutated_affine.nii") for patient in patients]
]

mri_img_paths = []
for arr in imgs:
    mri_img_paths += arr

print(mri_img_paths)


def resize(path: str, ref: str):
    nib_res = nib.load(path)
    nib_ref = nib.load(ref) 
    qfac = nib_res.header['pixdim'][0]
    px = nib_ref.header["pixdim"][1]
    py = nib_ref.header["pixdim"][2]
    pz = nib_ref.header["pixdim"][3]
    
    img_to_resize = ants.image_read(filename=path)

    resampled = ants.resample_image(image=img_to_resize, resample_params=(512, 512, 512), use_voxels=True)

    resized_fname = path[:-4] + "_resized.nii"
    ants.image_write(resampled, resized_fname)

    new_fname = resized_fname[:-4] + "_set_px.nii"

    set_pixdim_cmd = f"nifti_tool -mod_hdr -prefix {new_fname} -infiles {resized_fname} -mod_field pixdim '{qfac} {px} {py} {pz} 0.0 0.0 0.0 0.0'"
        
    os.system(set_pixdim_cmd)
    os.remove(resized_fname)
    os.rename(new_fname, resized_fname)

#resize("cohort/PIm0015/image_rbc2gas_binned_mutated_affine.nii", "cohort/PIm0015/CT_mask_neg_affine.nii")    

for img in mri_img_paths:
    resize(img, os.path.join(os.path.dirname(img), "CT_mask_neg_affine.nii"))     



