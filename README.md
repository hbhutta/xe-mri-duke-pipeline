If doing automatic segmentation, the manual seg file path does not need to be specified. Run the pipeline with:
```bash
python main.py \
    --config master_config.py \ [Required]
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
    --config master_config.py \ [Required]
    --force_recon \
    --data_dir ... \ [Required]
    --subject_id ... \ [Required]
    --rbc_m_ratio ... \ [Required]
```


### development notes 
If pip complains of insufficient disk space when installing packages, try:
- clearing up the tmp folder
- making assets an empty folder
- also make sure to delete the demo folder in assets



# Problems
- Dependencies and pip problem
  - Resolved by creating new virtual environment and installing all dependencies in one go from james' requirements.txt
  - first attempt: got pypdf not found 
- lobe split pi 8:
  - bias field works (image_cor.nii made), but problem in gas_binning
  - (128, 128, 128) size could result from resizing for CNN (segmentation.py)
- [jan 14, 2025] Getting Inputs do not occupy the same physical space! when running bias field correction, and then getting error in gas binning
  - Will see if using SimpleITK functions to set origin helps
  - Actually we are using the gas high reso as the image and the ct lobe mask part as the mask
  - Github (https://github.com/ANTsX/ANTs/wiki/Inputs-do-not-occupy-the-same-physical-space) says that perhaps calling antsApplyTransforms could resolve the issue
- [jan 15, 2025] clear tmp/ folder before re-running pipeline
# references:
- https://stackoverflow.com/questions/71268147/is-there-a-way-to-test-the-results-of-an-os-system-command-in-python


save the output of a script to a text file with:
`python foo.py 2>&1 | tee log.txt`

"foo_mutated_affine_resized.nii"

# Outline
1. Reconstruct all images (images will likely have dimensions 128x128x128 and pixdims around 0.03, matching mask_reg, which is correct, if not correct them in resizing step)
2. Reorient
3. Resize all reoriented mri-type images
4. Register reoriented CT and MRI
  - CT_mask_neg_affine.nii, mask_reg_edited_mutated_affine_warped.nii
5. Apply fwtransforms to reconstructed images (at this point they have been resized and reoriented)
6. Check images
7. Run stats.


In the `mask_reg_edited.nii` for PIm0377: (0.03125) -> mm scale
![alt text](image.png)
![alt text](image-1.png)

`mask_reg_edited.nii` for patients past PIm0288 (1.0) -> cm scale



after resizing, resized reconstructed images match mask_reg_edited
![alt text](image-2.png)
