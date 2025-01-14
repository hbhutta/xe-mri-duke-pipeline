"""Scripts to run gas exchange mapping pipeline."""
import logging
import glob 
import os

from absl import app, flags
from ml_collections import config_flags

from config import base_config
from subject_classmap import Subject

from utils import constants

from utils.img_utils import split_mask

from time import sleep


FLAGS = flags.FLAGS

_CONFIG = config_flags.DEFINE_config_file("config", None, "config file.")

flags.DEFINE_boolean(name="force_readin", 
                     default=False,
                     help="force read in .mat for the subject")

flags.DEFINE_boolean(name="force_recon", 
                     default=False,
                     help="force reconstruction for the subject")


flags.DEFINE_string(name="data_dir",
                    default=None, # assuming that this is where .dat files are stored by default
                    help="The folder where the .dat files are stored",
                    required=True)

flags.DEFINE_float(name="rbc_m_ratio",
                    default=None, 
                    help="The RBC:M ratio, calculated through a separate Matlab script",
                    required=True)

flags.DEFINE_string(name="subject_id",
                    default=None, 
                    help="The PIm registry ID of the subject to process",
                    required=True)

flags.DEFINE_bool(name="force_segmentation", 
                  default=False, 
                  help="run segmentation again.")

# flags.DEFINE_string(name="seg_path",
                    # default=None, 
                    # help="The path to the mask/label")





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
    subject.get_info()
    subject.save_subject_to_mat()
    subject.write_stats_to_csv()
    subject.generate_figures()
    subject.generate_pdf()
    subject.save_files()
    subject.save_config_as_json()
    subject.move_output_files()
    subject.copy_relevant_files()
    subject.zip_relevant_files()
    logging.info("Complete")


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
    config.data_dir = FLAGS.data_dir
    
    print(f"Given data directory: {config.data_dir}")
    
    # Set subject id 
    config.subject_id = FLAGS.subject_id
    print(f"Given subject ID: {config.subject_id}")
    
    # Set RBC:M ratio (calculated from a separate matlab script)
    '''
    
    '''
    config.rbc_m_ratio = FLAGS.rbc_m_ratio 
    print(f"Given RBC:M ratio: {config.rbc_m_ratio}")
    
    # Set manual or automatic segmentation
    if FLAGS.force_segmentation:
        config.segmentation_key = constants.SegmentationKey.CNN_VENT.value
        print(f"Enabled automatic segmentation, using {config.segmentation_key}")
    else:
        config.segmentation_key = constants.SegmentationKey.MANUAL_VENT.value
      
        # !!! 
        mask_file_paths = glob.glob(os.path.join(config.data_dir, "**mask**.nii"))
        for mfp in mask_file_paths:
            if ("CT_lobe_mask.nii" in mfp or "ct_corepeel_mask.nii" in mfp):
                split_mask(mask_image_file_path=mfp, save_imgs=True)
       
        # Glob for the first mask *after* generating splits 
        config.manual_seg_filepath = "data_dirs/PIm0075/CT_lobe_mask_split_PI_8.nii" # glob.glob(os.path.join(config.data_dir, "**mask**.nii"))[0] # ORIGINAL
        print(f"main.py: Disabled automatic segmentation, using {config.segmentation_key}")
        print(f"main.py: Given mask/label file: {config.manual_seg_filepath}")
    
    if not FLAGS.force_segmentation and not config.manual_seg_filepath:
        raise("File path for manual segmentation has not been set even though manual segmentation is enabled. Pipeline terminated.")
   
    # Confirm with user that the specified settings are correct 
    confirmation = input("Are the above settings correct? [Y/N]: ")
    if confirmation == "N":
        print("The above settings are not correct. Pipeline terminated.")
        return

    
    if FLAGS.force_recon or config.processes.gx_mapping_recon:
        print(f"force_recon: {FLAGS.force_recon}")
        print(
            f"config.processes.gx_mapping_recon: {config.processes.gx_mapping_recon}\n\n\n")
        gx_mapping_reconstruction(config)

    elif FLAGS.force_readin or config.processes.gx_mapping_readin:
        print(f"force_readin: {FLAGS.force_readin}")
        print(
            f"config.processes.gx_mapping_readin: {config.processes.gx_mapping_readin}\n\n\n")
        gx_mapping_readin(config)
    else:
        pass


if __name__ == "__main__":
    app.run(main)

