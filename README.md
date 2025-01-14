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
  - 