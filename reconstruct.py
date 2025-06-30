"""Scripts to run gas exchange mapping pipeline."""
import logging
import pickle
import os 
from time import sleep
from absl import app, flags
from ml_collections import config_flags

from config import base_config
from subject_classmap import Subject

FLAGS = flags.FLAGS

_CONFIG = config_flags.DEFINE_config_file("config", None, "config file.")

flags.DEFINE_boolean(name="force_recon", 
                     default=False,
                     help="force reconstruction for the subject")

flags.DEFINE_string(name="patient_path",
                    default=None, # assuming that this is where .dat files are stored by default
                    help="The folder where the .dat files are stored",
                    required=True)

#flags.DEFINE_string(name="msfp",
#                    default=None, # assuming that this is where .dat files are stored by default
#                    help="Manual segmentation file path",
#                    required=True)
#
flags.DEFINE_float(name="rbc_m_ratio",
                    default=None, 
                    help="The RBC:M ratio, calculated through a separate Matlab script",
                    required=True)

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
        
  
    # These are the images that *will* exist after the reconstruction step has been run
    patients = [config.data_dir]
    imgs = [
        [os.path.join(patient, "mask_reg_edited.nii") for patient in patients],
        [os.path.join(patient, "image_gas_highreso.nii") for patient in patients],
        [os.path.join(patient, "image_gas_binned.nii") for patient in patients],
        [os.path.join(patient, "image_gas_cor.nii") for patient in patients],
        [os.path.join(patient, "image_rbc2gas_binned.nii") for patient in patients],
        [os.path.join(patient, "image_rbc2gas.nii") for patient in patients],
        [os.path.join(patient, "mask_vent.nii") for patient in patients],
        [os.path.join(patient, "image_membrane.nii") for patient in patients],
        [os.path.join(patient, "image_membrane2gas_binned.nii") for patient in patients],
        [os.path.join(patient, "image_membrane2gas.nii") for patient in patients],
        [os.path.join(patient, "image_gas_binned.nii") for patient in patients]
    ]

    img_paths = []
    for img in imgs:
        img_paths += img

    are_files_reconstructed = True
    for img in img_paths:
        if (not os.path.isfile(img)):
            are_files_reconstructed = False
            logging.info(f"File {img} does not exist. Will redo reconstruction.")
            sleep(10) 
            break

    if (not are_files_reconstructed):
        subject.calculate_rbc_m_ratio()
        logging.info("Reconstructing images")
        subject.preprocess()
        subject.reconstruction_gas()
        subject.reconstruction_dissolved() 
    
        if config.recon.recon_proton:
            subject.reconstruction_ute()
       
        # self.mask is set to mask_reg_edited here
        subject.segmentation() 
        
        subject.registration()
        subject.biasfield_correction() 
        subject.gas_binning() 
        subject.dixon_decomposition() 
        subject.hb_correction()
        subject.dissolved_analysis()
        subject.dissolved_binning()
        
        subject.save_files()
    
        # dict_dis is being created because it contains information needed in computing stats   
        with open(f'{subject.config.data_dir}/dict_dis.pkl', 'wb') as f:  # open a text file
             pickle.dump(subject.dict_dis, f) # serialize the list

    if (not are_files_reconstructed):
        logging.info("Done. No reconstruction occurred.")
    else: 
        logging.info("Done. Reconstructed files.")

def main(argv):
    print("reconstruct.py: in main()")
    """Run the gas exchange imaging pipeline.

    Either run the reconstruction or read in the .mat file.
    """
    config = _CONFIG.value

    # Set data dir from flag argument

    config.data_dir = FLAGS.patient_path
    config.rbc_m_ratio = FLAGS.rbc_m_ratio
    config.manual_seg_filepath = f"{config.data_dir}/mask_reg_edited.nii"

    print(f"reconstruct.py got data_dir: {config.data_dir}")
    print(f"reconstruct.py got rbc_m_ratio: {config.rbc_m_ratio}")
    print(f"reconstruct.py got manual_seg_filepath: {config.manual_seg_filepath}")

    if FLAGS.force_recon or config.processes.gx_mapping_recon:
        print(f"force_recon: {FLAGS.force_recon}")
        print(
            f"config.processes.gx_mapping_recon: {config.processes.gx_mapping_recon}\n\n\n")
        gx_mapping_reconstruction(config=config)
    else:
        pass

if __name__ == "__main__":
    app.run(main)