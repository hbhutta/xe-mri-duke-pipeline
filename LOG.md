# Development log

## June 16, 2025 (Monday)
- Ensure that the correct conda environment is being used as incorrect package versions can cause internal errors
- First working version of pipeline is commit d3294af2a06f7af9b617907eecf67590caca17bc
- Entire pipeline seems to run without errors when the xe-mri conda environment is used
- Some problems in the generated csv file for PIm0038:
  1. `membrane_defect_pct` is 0.0 for all rows
  2. `vent_low_pct` is greater than 100 for row 5
  3. Rows are unnamed
  4. Column sums should be included and should add up to the whole lung average
- The csv rows should be named as:
    - LUL_8
    - LLL_16
    - RUL_32
    - RML_64
    - RLL_128
    - CORE_40
    - PEEL_50
    - WHOLE_LUNG_AVG  
- Each csv file can always be edited after being created for these names to appear
- Row for whole lung average is currently missing from csv file
- The lobar averages should sum to the whole lung average
- Check for anything unusual in the nifti images produced from taking the product between the mask and the warped image
- Tested PIm0067 as well, exact same problems in csv file
- The row for right-middle lob seems weird as some values are percentages are greater than 100 (maybe this is fine?)
- Tested PIm0078, this time membrane_defect_pct has values but membrane_high_pct is zero
- When should we use mask_vent as opposed to mask in calculating the bin percentages? (e.g. for RBC_MEAN we use mask_vent and for MEMBRANE_DEFECT_PCT we used mask)
  - What exactly are mask and mask_vent?
- We are using mask_vent for MEMBRANE_MEAN and all those values seem reasonable (roughly the same for all seven sections)

Lines from 2025_06_16_PIm0078.txt showing 12 values being computed for the first row (left upper lobe)
```txt
Processing split cohort/PIm0078/CT_lobe_mask_neg_affine_split_PI_8.nii
Reading #1 from cohort/PIm0078/mask_vent_mutated_affine_resized_warped.nii
Reading #2 from cohort/PIm0078/CT_lobe_mask_neg_affine_split_PI_8.nii
Multiplying #2 and #1
Writing #1 to file cohort/PIm0078/CT_lobe_mask_neg_affine_split_PI_8_product.nii
  Output voxel type: float[f]
  Rounding off: Disabled
computing bin_percentage
computing bin_percentage
computing bin_percentage
computing mean
mean(): image.shape = (512, 512, 429)
mean(): mask.shape = (512, 512, 429)
Computed mean: 0.7070444012228689
computing bin_percentage
computing bin_percentage
computing bin_percentage
computing mean
mean(): image.shape = (512, 512, 429)
mean(): mask.shape = (512, 512, 429)
Computed mean: 0.0054452209920320275
computing bin_percentage <-- membrane_defect_pct
computing bin_percentage <-- membrane_low_pct
computing bin_percentage <-- membrane_high_pct
computing mean
mean(): image.shape = (512, 512, 429)
mean(): mask.shape = (512, 512, 429)
Computed mean: 0.00737464678215138
Processing split cohort/PIm0078/CT_lobe_mask_neg_affine_split_PI_16.nii
```

- Also bin percentages being zero might not necessarily be a bad thing
- The safe assumption is that if all other bin percentages are being computed, and they seem reasonable, and a certain defect percentage (e.g. membrande_low_pct) is all zero only sometimes, then this may be fine. (Alex can confirm by looking at the patients)

## June 17, 2025 (Tuesday)
- In `stats.py` wrote a line which adds the CT_mask.nii (the mask which captures the whole lung) to the `splits` array, so that before the `for` loop the `splits` array now has eight strings, the last string being a path to the whole-lung mask. 
  - Still have problems with this line, perhaps product computed in `stats.py` is wrong
  - So there will be now be eight rows in the csv files; the last row being the whole lung average stats
- Resolved a major confusion between `self.mask` and `self.mask_vent` in `subject_classmap.py`
  - The former is the mask including the defect areas while the later does not include defect areas
  - In calculating RBC and membrane signal, we want defect regions to be excluded because defected areas obviously will not have any signal. 
    - We are interested in RBC and membrane signal in only non-defective areas of the lungs
    - In other words, we should use `self.mask_vent` for RBC and membrane defect percentage calculations
  - However for ventilation signal (i.e. how much and where gas is diffusing through the lung), we should use `self.mask` because here we deliberately want to include how much of the lung is non-functioning in our calculations

- An example of how all the CT masks, mask_reg_edited and mask_vent should match after reorientation, resizing and registration:
![alt text](images/PIm0078_example_matching_images_after_registration.png)
- In this example the difference between the mask_reg_edited and mask_vent is very little but PIm0078 (which this example is from) also has nearly neglibile ventilation defect
- Keep PIm0350 in mind for someone with very high ventilation defect (entire right lung almost defect)
- Even though I used self.mask_vent which for RBC and membrane signal calculation (a change I made today), and this is correct, there is little change in the values (for PIm0025)
  - This is expected because PIm0025 specifically has very little ventilation defect (as per pdf in V2 results in registry folder)

```txt
Processing split cohort/PIm0025/CT_lobe_mask_neg_affine_split_PI_8.nii
Reading #1 from cohort/PIm0025/mask_vent_mutated_affine_resized_warped.nii
Reading #2 from cohort/PIm0025/CT_lobe_mask_neg_affine_split_PI_8.nii
```

## June 18, 2025 (Wednesday)
- What exactly do the bins mean in computing the bin_percentages? Are they pixel intensities or are they labels?
  - How does the binning work 
  - Why is that using the split of the binned image instead of the entire binned image is what results in the `volume_in_bins` quantity being zero?
  - The number 1 in `np.ndarray([1])` cannot be a pixel intensity because then it would appear very darkly in the image
  - The other numbers such as 6, 7 and 8 as well; none of them can be pixel intensities; they are likely labels for something
  - Nevermind??? Maybe they are pixel intensities? I just checked them.
    - Actually no the PIs in the binned image are mostly discrete whole numbers
    - There are also some voxels with fractional pixel intensities (e.g. 3.005 instead of 3), so this voxel would not be included in the quantity of voxels that fall into the bin based on the strict calculation of the da.isin function (np.isin)
- Realized that I had appended CT_mask.nii instead of CT_mask_neg_affine.nii to the `splits` array in `stats.py`
```txt
Processing split cohort/PIm0025/CT_mask.nii
pixdim[0] (qfac) should be 1 (default) or -1; setting qfac to 1
I0618 18:14:03.577603 140388223358784 batteryrunners.py:268] pixdim[0] (qfac) should be 1 (default) or -1; setting qfac to 1
Reading #1 from cohort/PIm0025/mask_vent_mutated_affine_resized_warped.nii
Reading #2 from cohort/PIm0025/CT_mask.nii
Multiplying #2 and #1
Exception caught of type N3itk15ExceptionObjectE
  Exception detail: /data/hippogang/build/buildbot/Nightly/itk/v5.2.1/itk/Modules/Core/Common/include/itkImageToImageFilter.hxx:219:
ITK ERROR: MultiplyImageFilter(0x555fe54accb0): Inputs do not occupy the same physical space! 
InputImage Origin: [0.0000000e+00, 0.0000000e+00, 0.0000000e+00], InputImage_1 Origin: [-1.7615524e+02, 1.7615524e+02, -1.5800000e+02]
	Tolerance: 6.8945301e-05
InputImage Direction: 1.0000000e+00 0.0000000e+00 0.0000000e+00
0.0000000e+00 1.0000000e+00 0.0000000e+00
0.0000000e+00 0.0000000e+00 1.0000000e+00
, InputImage_1 Direction: 1.0000000e+00 0.0000000e+00 0.0000000e+00
0.0000000e+00 1.0000000e+00 0.0000000e+00
0.0000000e+00 0.0000000e+00 -1.0000000e+00

	Tolerance: 1.0000000e-04

Traceback (most recent call last):
  File "/home/hbhutta/miniconda3/envs/xe-mri/lib/python3.8/site-packages/nibabel/loadsave.py", line 100, in load
    stat_result = os.stat(filename)
FileNotFoundError: [Errno 2] No such file or directory: 'cohort/PIm0025/mask_vent_mutated_affine_resized_warped__CT_mask_product.nii'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "stats.py", line 355, in <module>
    app.run(main)
  File "/home/hbhutta/miniconda3/envs/xe-mri/lib/python3.8/site-packages/absl/app.py", line 308, in run
    _run_main(main, args)
  File "/home/hbhutta/miniconda3/envs/xe-mri/lib/python3.8/site-packages/absl/app.py", line 254, in _run_main
    sys.exit(main(argv))
  File "stats.py", line 347, in main
    compute_patient_stats(config)
  File "stats.py", line 241, in compute_patient_stats
    subject.mask_vent = nib.load(
  File "/home/hbhutta/miniconda3/envs/xe-mri/lib/python3.8/site-packages/nibabel/loadsave.py", line 102, in load
    raise FileNotFoundError(f"No such file or no access: '{filename}'")
FileNotFoundError: No such file or no access: 'cohort/PIm0025/mask_vent_mutated_affine_resized_warped__CT_mask_product.nii'
```

- For each split and any binned image (e.g. image_rbc2gas_binned, image_gas_binned), check if there really is multiplication by the pixel intensity of the split, or if this is just coincidence
  - e.g. for PIm0025 check for PIs 64 and 128
- Division by PI likely not needed for mean calculations ?
- `membrane_high_pct` is still 0.0 in all rows

Code for computing `membrane_high_pct`:

```python
constants.StatsIOFields.MEMBRANE_HIGH_PCT: metrics.bin_percentage(
    self.image_membrane2gas_binned, np.array([6, 7, 8]), self.mask_vent # previously self.mask
    # self.image_membrane2gas_binned, np.array([48, 56, 64]), self.mask_vent # previously self.mask
),
```

If membrane_high_pct is consistently 0.0 in the CSV file, it means that the pixel intensities 6, 7 and 8 
are not in the image_membrane2gas_binned (i.e. no region of this image is falling into these bins).
In other words, volume_in_bins is 0 (the volume of the mask is an invariant for any given split)

## June 19, 2025 (Thursday)
- Pixel intensity chosen for whole lung might not be correct
- Say `** ERROR: NWAD 0 out of ... bytes to file` in run #1 of PIm0038 but did not see this in runs for other subjects 
- 
## June 19, 2025 (Friday)
- When computing whole lung average, the right lung has PI 30 and the left lung has PI 20
  - One solution is to set all the non-zero PIs in this mask to 1 because we need to distinguish between left lung and right lung statistics
  - This was the solution, stats showing up for original CT mask now
- For PIm0025
  - Computing stats alone takes half the average time for a run (16 mins out of ~30 mins)
  - Regional measurements still do not add up to the whole lung measurements obtained here, will try another patient
- 



