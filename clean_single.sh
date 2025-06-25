#!/bin/bash

: '
Author: Haad Bhutta
Created: June 12, 2025

Description:
This script is used with pipeline_single.sh to remove files generated in 
the pipeline for testing purposes. It is recommended to use this file when 
testing changes to the pipeline to see how the generated files are affected.

Example usage:
bash clean_single.sh cohort/PIm1234
'
dir=$1

rm -rf $dir/image_* # Removes all reconstructed images
rm -rf $dir/mask_reg_edited_* # Keeps original mask_reg_edited but removes the reoriented and resized versions as these may change
rm -rf $dir/mask_vent_* # Same thing happens above
rm -rf $dir/mask_reg.nii # This may or may not be generated in reconstruction but it is removed
rm -rf $dir/CT_mask_*
rm -rf $dir/CT_lobe_mask_*
rm -rf $dir/ct_corepeel_mask_*
rm -rf $dir/*_vent.pkl 
rm -rf $dir/*_reg.pkl # Optionally, remove the previous registration
