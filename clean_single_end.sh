#!/bin/bash

: '
Author: Haad Bhutta
Updated: June 30, 2025

Description:
This script is used with pipeline_single.sh to remove files generated in 
the pipeline for testing purposes. It is recommended to use this file when 
testing changes to the pipeline to see how the generated files are affected.

Importantly, if the regional measurements have already been computed,
this script will not remove them and the pipeline will not re-compute them.

Example usage:
bash clean_single.sh cohort/PIm1234
'
dir=$1

set -euo pipefail

rm -rf $dir/image_* # Removes all reconstructed images

# For the same reasons as the CT mask, the resized and reoriented versions of these two masks do not need to be removed.
rm -rf $dir/mask_reg_edited_* 
rm -rf $dir/mask_vent_* 

# Safest to keep this, whatever this is; it may or may not be generated in reconstruction but it is removed

rm -rf $dir/mask_reg.nii 

# The CT masks do not need to be removed because the only changes they will go through are resizing and reorienting, and these steps are finished, so they will never be changed again.
rm -rf $dir/CT_mask_*
rm -rf $dir/CT_lobe_mask_*
rm -rf $dir/ct_corepeel_mask_*

# It's a good idea to re-generated dict_dis because it contains information like the field of view which is used in indirectly used in computing stats
rm -rf $dir/dict_dis.pkl # This contains information needed in computing stats

# Optionally, remove the previous registration for mask and mask_vent
# rm -rf $dir/*_vent.pkl 
# rm -rf $dir/*_reg.pkl 

# WARNING: Make sure to remove this line once pipeline is finalized

# Remove 'Core' and 'Peel' directories if they exist
rm -rf $dir/Core
rm -rf $dir/Peel
