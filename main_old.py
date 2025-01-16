"""Scripts to run gas exchange mapping pipeline."""
import logging
import glob 
import os

from absl import app, flags
from ml_collections import config_flags
import ants
import numpy as np

from config import base_config
from subject_classmap import Subject

from utils import constants

from time import sleep

FLAGS = flags.FLAGS

_CONFIG = config_flags.DEFINE_config_file("config", None, "config file.")

flags.DEFINE_boolean(name="force_readin", 
                     default=False,
                     help="force read in .mat for the subject")

flags.DEFINE_boolean(name="force_recon", 
                     default=False,
                     help="force reconstruction for the subject")

flags.DEFINE_bool(name="force_segmentation", 
                  default=False, 
                  help="run segmentation again.")



def gx_mapping_reconstruction(config: base_config.Config):
    """Run the gas exchange mapping pipeline with reconstruction.

    Args:
        config (config_dict.ConfigDict): config dict
    """
    subject = Subject(config=config)
    try:
        subject.read_twix_files()
    except:
        logging.warning("Cannot read in twix files.")
        try:
            subject.read_mrd_files()
        except:
            raise ValueError("Cannot read in raw data files.")
    subject.calculate_rbc_m_ratio()
    logging.info("Reconstructing images")
    
    # Preprocess only necessary if calling reconstruct funcs$
    rel_dir = f"data_dirs/{config.subject_id}_relevant_files/"
#    items = [
#        rel_dir + "gas_highreso.nii",
#        rel_dir + "rbc2gas.nii",
#        rel_dir + "membrane2gas.nii"
#    ]
    
    if (not os.path.isdir(rel_dir)):
        print(f"Recon files do not exist, starting recon...")
        subject.preprocess()
        subject.reconstruction_gas()
        subject.reconstruction_dissolved() 

        if config.recon.recon_proton:
            subject.reconstruction_ute()
    else:
        print(f"Reconstructed files already exist, skipping recon...")    
    # At this point ensure that all files in the temp list are in tmp/
    print(glob.glob(os.path.join("tmp/", "*.nii")))
        
    subject.segmentation() 

    '''
    After running segmentation, we should have the mask_reg,
    assuming the pipeline was run with CNN_VENT enabled
    '''
    print(glob.glob(os.path.join("tmp/", "*.nii")))


    # this should be looped 8 times (for each ct mask, lobe core peel)
    # ai should produce mask reg (last point for initial run)
    
    # We need to register mask 2 gas to ensure matching sizes for biasfield correction
    subject.registration()
    subject.biasfield_correction() # !!!!! Missing image_cor (bias field correction didn't generate output)
    subject.gas_binning() # !!!!! IndexError
    subject.dixon_decomposition() # image_dissolved and gas_highsnr used here
    subject.hb_correction()
    subject.dissolved_analysis()
    subject.dissolved_binning()
   
    """
    Computing statistics in get_statistics() uses specific images:
    - self.image_gas_binned
    - self.image_membrane2gas_binned
    - self.image_rbc2gas_binned
    - self.image_rbc2gas
    - self.image_membrane2gas
    - self.image_gas_cor
    - self.mask
    - self.mask_vent
    
    Note that these attributes are of type np.ndarray.
   
    To get the np.ndarray of a NIFTI image called 'img' we can do this:
    
    img = nib.load(img_path)
    img_data = img.get_fdata()
   
    If registration is done by this point and these images are warped 
    based on the fwdtransforms, we can apply the CT mask splits 
    (e.g. core, peel, five lobes) and run the functions:
    - subject.get_statistics()
    - subject.write_stats_to_csv()
    
    We have to apply the forward transforms from registration onto 
    the images above before applying the mask
    
    We may want to use ANTS functions to read/write images
    instead of nibabel functions because we will ultimately use
    antsApplyTransform to apply the forward transforms to the images
    
    For each of:
    - Core
    - Peel
    - RUL (right upper lobe)
    - RLL (right lower lobe)
    - RML (right middle lobe)
    - LLL (left lower lobe)
    - LUL (left upper lobe)
    
    We shouldn't overwrite the csv at every call to write_stats_to_csv
   
    The outer for-loop loops over every split.
    The inner for loops loops over every relevant image.
    
    ANTS functions of interest are:
    - numpy(): to get underlying data for image
        - if this doesn't work, we can nib.load then get_fdata
    - mask_image(target, mask): applies mask to target, both ANTS images
    - image_read(filename): reads an ANTS image from a filename
    
    fwdtransforms only need to be applied once, its doesn't depend on a split
    """
   
    # We should have saved files in tmp/ beforehand 
    subject.save_files()
    
    # 3.8.8 glob doesn't accept root-dir
    splits = glob.glob(f"{config.data_dir}/*split*")    
   
    imgs = [ 
        ants.image_read("tmp/image_membrane2gas_binned.nii"),
        ants.image_read("tmp/image_rbc2gas_binned.nii"),
        ants.image_read("tmp/image_rbc2gas.nii"),
        ants.image_read("tmp/image_membrane2gas.nii"),
        ants.image_read("tmp/image_gas_cor.nii"),
        ants.image_read("tmp/mask.nii"),
        ants.image_read("tmp/mask_vent.nii")
    ] 
    # This can be threaded
    for img in imgs:
        apply_transforms(target=img, transformlist=...)
    
    
    for split in splits:
       
       
        for img in imgs:
            apply_mask(target=img.data, mask=split)
    

        # apply ft to anything called by statistics (used in report)
        subject.get_statistics()
        subject.get_info()
        
        # To write 8 rows to one csv file, ensure overwrite is False
        # But avoid re-writing the header everytime 
        # (already taken care of in overwrite=False case)
        subject.write_stats_to_csv()
        
    logging.info("Complete")


def apply_mask(target: np.ndarray, mask: np.ndarray) -> None:
    """Multiplies mask into target
    
    Args:
    target (np.ndarray): The target to apply the mask onto
    mask (np.ndarray): The mask
    """
    pass


def gx_mapping_readin(config: base_config.Config):
    """Run the gas exchange imaging pipeline by reading in .mat file.

    Args:
        config (config_dict.ConfigDict): config dict
    """
    subject = Subject(config=config)
    subject.read_mat_file()
    if FLAGS.force_segmentation:
        subject.segmentation()
    subject.gas_binning()
    subject.dixon_decomposition()
    subject.hb_correction()
    subject.dissolved_analysis()
    subject.dissolved_binning()
    subject.get_statistics()
    subject.get_info()
    subject.save_subject_to_mat()
    subject.write_stats_to_csv()
    subject.generate_figures()
    subject.generate_pdf()
    subject.save_files()
    subject.save_config_as_json()
    subject.move_output_files()
    logging.info("Complete")


def main(argv):
    """Run the gas exchange imaging pipeline.

    Either run the reconstruction or read in the .mat file.
    """
    config = _CONFIG.value

    # Set data dir from flag argument
       
    if FLAGS.force_recon or config.processes.gx_mapping_recon:
        print(f"force_recon: {FLAGS.force_recon}")
        print(
            f"config.processes.gx_mapping_recon: {config.processes.gx_mapping_recon}\n\n\n")
        proceed = input("Proceed [Y/N]? ")
        if (proceed == "Y"):
            gx_mapping_reconstruction(config)
        else:
            pass

    elif FLAGS.force_readin or config.processes.gx_mapping_readin:
        print(f"force_readin: {FLAGS.force_readin}")
        print(
            f"config.processes.gx_mapping_readin: {config.processes.gx_mapping_readin}\n\n\n")
        gx_mapping_readin(config)
    else:
        pass


if __name__ == "__main__":
    app.run(main)



"""
If doing automatic segmentation, the manual seg file path does not need to be specified. Run the pipeline with:
```bash
python main.py \
    --config master_config.py \
    --force_recon \
    --data_dir ... \ [Required]
    --subject_id ... \ [Required]
    --rbc_m_ratio ... \ [Required]
    --force_segmentation 
```
    
If doing manual segmentation (i.e. the --force_segmentation flag is not enabled) it is assumed that the mask file is stored in the data_dir and 
that the filename of the mask has the word "mask" in it. Run the pipeline with:
```bash
python main.py \
    --config master_config.py \
    --force_recon \
    --data_dir ... \
    --subject_id ... \
    --rbc_m_ratio ... \
```
"""