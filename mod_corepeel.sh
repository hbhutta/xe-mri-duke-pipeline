#/bin/bash
#  .182709
dir=$1

nifti_tool -mod_hdr -mod_field pixdim '-1.0 0.634766 0.634766 1.25 0.0 0.0 0.0 0.0' -prefix $dir/ct_corepeel_mask_neg_affine_mod.nii -infiles $dir/ct_corepeel_mask_neg_affine.nii 
nifti_tool -mod_hdr -mod_field qoffset_x 162.182709 -prefix $dir/ct_corepeel_mask_neg_affine_mod_x.nii -infiles $dir/ct_corepeel_mask_neg_affine_mod.nii 
nifti_tool -mod_hdr -mod_field qoffset_y -162.182709 -prefix $dir/ct_corepeel_mask_neg_affine_mod_x_y.nii -infiles $dir/ct_corepeel_mask_neg_affine_mod_x.nii 
nifti_tool -mod_hdr -mod_field qoffset_z -137.5 -prefix $dir/ct_corepeel_mask_neg_affine_mod_x_y_z.nii -infiles $dir/ct_corepeel_mask_neg_affine_mod_x_y.nii 

#mv $dir/ct_corepeel_mask_neg_affine_mod_x_y_z.nii
#$dir/ct_corepeel_mask_neg_affine_mod.nii

