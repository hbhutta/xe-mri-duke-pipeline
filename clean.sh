#!/bin/bash
dir=$1

if [[ $dir == "" ]]; then
  echo "empty dir"
  exit 1
fi

rm -rf $dir/image_*
rm -rf $dir/mask_reg_edited_*
rm -rf $dir/mask_vent_*
rm -rf $dir/mask_reg.nii
rm -rf $dir/CT_lobe_mask_neg_affine_*
rm -rf $dir/ct_corepeel_mask_neg_affine_*
