import nibabel as nib
import os
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

def resize_mri(mri_path: str, ct_path: str) -> None:
    resized_mri_path = mri_path[:-4] + "_resized.nii"
    if os.path.isfile(resized_mri_path):
        print(f"resize.py, resize_mri(): File {mri_path} already resized.") 
        return
   
    # Load target MRI image and reference CT image 
    nib_mri = nib.load(mri_path)
    nib_ref = nib.load(ct_path)
    
    # Get the attributes needed fore resizing 
    qfac = nib_mri.header["pixdim"][0]
    px = nib_ref.header["pixdim"][1]
    py = nib_ref.header["pixdim"][2]
    pz = nib_ref.header["pixdim"][3]

    img_to_resize = ants.image_read(filename=mri_path)
    resampled = ants.resample_image(
        image=img_to_resize, resample_params=(512, 512, 512), use_voxels=True
    )
    
    # Directly modify NIFTI headers and rename resized file
    ants.image_write(resampled, resized_mri_path)
    new_fname = resized_mri_path[:-4] + "_set_px.nii"
    set_pixdim_cmd = f"nifti_tool -mod_hdr -prefix {new_fname} -infiles {resized_mri_path} -mod_field pixdim '{qfac} {px} {py} {pz} 0.0 0.0 0.0 0.0'"
    os.system(set_pixdim_cmd)
    os.remove(resized_mri_path)
    os.rename(new_fname, resized_mri_path)
    
    print(f"resize.py, resize_mri(): Resized {mri_path} to {resized_mri_path}")


def resize_mris(patient_path: str) -> None:
    # Enumerate all reoriented MRI-type images that need to be resized for later stats computation
    reoriented_mri_names = [
        "mask_reg_edited_mutated_affine.nii",
        "image_gas_highreso_mutated_affine.nii",
        "image_gas_binned_mutated_affine.nii",
        "image_gas_cor_mutated_affine.nii",
        "image_rbc2gas_binned_mutated_affine.nii",
        "image_rbc2gas_mutated_affine.nii",
        "mask_vent_mutated_affine.nii",
        "image_membrane_mutated_affine.nii",
        "image_membrane2gas_binned_mutated_affine.nii",
        "image_membrane2gas_mutated_affine.nii",
        "image_gas_binned_mutated_affine.nii",
    ]
    reoriented_mri_paths = [os.path.join(patient_path, name) for name in reoriented_mri_names]
   
    # Reference CT mask path to base resizing on 
    ct_path = os.path.join(patient_path, "CT_mask_neg_affine.nii")
    if not os.path.isfile(ct_path):
        raise FileNotFoundError(f"CT mask file {ct_path} does not exist.")
    
    # Resize each MRI-type image, first checking if it exists 
    for mri_path in reoriented_mri_paths:
        # If the image does not exist, terminate
        if not os.path.isfile(mri_path):
            raise FileNotFoundError(f"Reoriented MRI file {mri_path} needs to be resized for later stats computation, but does not exist.")
       
        # If the image does exist and is already resized, skip resizing to save some time 
        resized_mri_path = mri_path[:-4] + "_resized.nii"
        if os.path.isfile(resized_mri_path):
            print(f"resize.py, resize_mris(): File {mri_path} already resized.")
            continue
        resize_mri(mri_path=mri_path, ct_path=ct_path)

def main(argv):
    config = _CONFIG.value
    config.data_dir = FLAGS.patient_path
    patient_path = config.data_dir
    
    print("resize.py: Patient_path:", patient_path)

    resize_mris(patient_path=patient_path)

if __name__ == "__main__":
    # input("Running resize.py. Press Enter to continue...")
    app.run(main)
