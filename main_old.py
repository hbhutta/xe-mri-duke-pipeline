"""Scripts to run gas exchange mapping pipeline."""
import logging
import glob 
import os

from absl import app, flags
from ml_collections import config_flags

from config import base_config
from subject_classmap import Subject

from utils import constants

from register import register
from warp_vent import warp_image

import pickle

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
    
    subject.preprocess()
    subject.reconstruction_gas()
    subject.reconstruction_dissolved() 

    if config.recon.recon_proton:
        subject.reconstruction_ute()
    
    subject.segmentation() 

    subject.registration()
    subject.biasfield_correction() 
    subject.gas_binning()  
    subject.dixon_decomposition() 
    subject.hb_correction()
    subject.dissolved_analysis()
    subject.dissolved_binning()
  
    subject.get_statistics()
#    subject.get_info()
#    subject.save_subject_to_mat()
    subject.write_stats_to_csv()
#    subject.generate_figures()
#    subject.generate_pdf()
    subject.save_files()
#    subject.save_config_as_json()
    subject.move_output_files()
#    subject.copy_relevant_files()
#    subject.zip_relevant_files()
    logging.info("Complete")
    
    # Register CT mask to mask_reg_edited
    out_path = f"{config.dat_dir}/output/"
    
    reg_path = os.path.join(out_path, f"{config.subject_id}_reg.pkl")
    
    ct_mask = f"{config.data_dir}/CT_lobe_mask.nii"
    mask_reg = f"{config.data_dir}/mask_reg_edited.nii"

    # load forward transforms into a variable for use in warp_image    
    with open(reg_path, "rb") as file:
        mytx = pickle.load(file)

    # Threading here?
    gas_imgs = [
        os.path.join(out_path, "membrane2gas.nii"),
        os.path.join(out_path, "membrane2gas_binned.nii"),
        os.path.join(out_path, "membrane2gas_rgb.nii"),
        os.path.join(out_path, "rbc2gas.nii"),
        os.path.join(out_path, "rbc2gas_binned.nii"),
        os.path.join(out_path, "rbc2gas_rgb.nii"),
        os.path.join(out_path, "gas_binned.nii"),
        os.path.join(out_path, "gas_highreso.nii"),
    ]
  
    for gas_img in gas_imgs:  
        warp_image(fixed=ct_mask, moving=gas_img,
                            transform_list=mytx['fwdtransforms'])
        
    


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