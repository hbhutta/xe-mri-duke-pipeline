"""Scripts to run gas exchange mapping pipeline."""
import logging

from absl import app, flags
from ml_collections import config_flags

from config import base_config
from subject_classmap import Subject

import os

FLAGS = flags.FLAGS

_CONFIG = config_flags.DEFINE_config_file("config", None, "config file.")

def compute_patient_stats(config: base_config.Config):
    """Compute statistics for the patient

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

    Args:
        config (config_dict.ConfigDict): config dict
    """
 
    subject = Subject(config=config)
    
    # These must all be resized before 
    subject.mask = os.path.join(subject.config.data_dir, "mask_reg_edited.nii")
    subject.image_gas_highreso = os.path.join(subject.config.data_dir, "image_gas_highreso.nii")
    subject.image_gas_binned = os.path.join(subject.config.data_dir, "image_gas_binned.nii")
    subject.image_gas_cor = os.path.join(subject.config.data_dir, "image_gas_cor.nii")
    subject.image_rbc2gas_binned = os.path.join(subject.config.data_dir, "image_rbc2gas_binned.nii")
    subject.image_rbc2gas = os.path.join(subject.config.data_dir, "image_rbc2gas.nii")
    subject.mask_vent = os.path.join(subject.config.data_dir, "mask_vent.nii")
    subject.image_membrane = os.path.join(subject.config.data_dir, "image_membrane.nii")
    subject.image_membrane2gas_binned = os.path.join(subject.config.data_dir, "image_membrane2gas_binned.nii")
    subject.image_membrane2gas = os.path.join(subject.config.data_dir, "image_membrane2gas.nii")
    subject.image_gas_binned = os.path.join(subject.config.data_dir, "image_gas_binned.nii")
     
      
    subject.get_statistics()
    subject.write_stats_to_csv()
        
    logging.info("Complete") 
    
def main(argv):
    """Run the gas exchange imaging pipeline.

    Either run the reconstruction or read in the .mat file.
    """
    config = _CONFIG.value

    # Set data dir from flag argument
    compute_patient_stats(config)

if __name__ == "__main__":
    app.run(main)



"""
Run with
```bash
python stats.py --config master_config.py \
```
``
"""