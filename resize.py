import nibabel as nib 
import os
import ants 
from sys import argv

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


if len(argv) < 2:
    print("Usage: python resize.py <patient_path>")
    exit(1)
    
patient_path = argv[1] # patient path

# This script assumes the following files exist:
mri_type_image_paths = [
   os.path.join(patient_path, "mask_reg_edited_mutated_affine.nii"),
    os.path.join(patient_path, "image_gas_highreso_mutated_affine.nii"),
    os.path.join(patient_path, "image_gas_binned_mutated_affine.nii"),
    os.path.join(patient_path, "image_gas_cor_mutated_affine.nii"),
    os.path.join(patient_path, "image_rbc2gas_binned_mutated_affine.nii"),
    os.path.join(patient_path, "image_rbc2gas_mutated_affine.nii"),
    os.path.join(patient_path, "mask_vent_mutated_affine.nii"),
    os.path.join(patient_path, "image_membrane_mutated_affine.nii"),
    os.path.join(patient_path, "image_membrane2gas_binned_mutated_affine.nii"),
    os.path.join(patient_path, "image_membrane2gas_mutated_affine.nii"),
    os.path.join(patient_path, "image_gas_binned_mutated_affine.nii"),
]

are_mris_resized = True
for img in mri_type_image_paths:
    if (not os.path.isfile(img[:-4] + "_resized.nii")):
        are_mris_resized = False
        print(f"File {img} does not exist. Will redo resizing of all MRI images.")
        break

if (not are_mris_resized):
    print(f"resize.py: Resizing MRI images for patient {patient_path}")
    for img in mri_type_image_paths:
        print(f"Resizing image {img}")
        if (not os.path.isfile(img[:-4] + "_resized.nii")):
            resize(img, os.path.join(os.path.dirname(img),
                "CT_mask_neg_affine.nii"))     
        else:
            print(f"File {img} already resized")
else:
    print("All MRI images already resized for patient {patient_path}. No resizing needed.") 


