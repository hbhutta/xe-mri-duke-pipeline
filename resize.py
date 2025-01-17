import nibabel as nib 
import os
import ants 

def resize(path: str):
    nib_res = nib.load(path)
    
    qfac = nib_res.header['pixdim'][0]
    px = nib_res.header["pixdim"][1]
    py = nib_res.header["pixdim"][2]
    pz = nib_res.header["pixdim"][3]
    
    img_to_resize = ants.image_read(filename=path)

    resampled = ants.resample_image(image=img_to_resize, resample_params=(512, 512, 512), use_voxels=True)

    resized_fname = path[:-4] + "_resized.nii"
    ants.image_write(resampled, resized_fname)

    new_fname = resized_fname[:-4] + "_set_px.nii"

    set_pixdim_cmd = f"nifti_tool -mod_hdr -prefix {new_fname} -infiles {resized_fname} -mod_field pixdim '{qfac} {px} {py} {pz} 0.0 0.0 0.0 0.0'"
    os.system(set_pixdim_cmd)
    os.remove(resized_fname)
     
ct_mask = "cohort/PIm0015/CT_mask_neg_affine.nii" 
mri = "cohort/PIm0015/mask_reg_edited.nii" 

resize(mri)


