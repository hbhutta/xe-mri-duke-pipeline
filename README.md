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