"""Metrics for evaluating images."""

import heapq
import cv2
import numpy as np
from scipy import ndimage
from scipy.ndimage.morphology import binary_dilation
from utils import constants
import math
import sys
from datetime import datetime
import dask.array as da

# from dask.diagnostics import ProgressBar
from dask import config

config.set(scheduler="threads")

sys.path.append("..")


def _get_dilation_kernel(x: int) -> int:
    """Get dilation kernel for binary dilation in 1-dimension."""
    return int((math.ceil(x * 0.025) * 2 + 1))


def snr(image: np.ndarray, mask: np.ndarray, window_size: int = 8):
    print("computing snr")
    """Calculate SNR using sliding windows.

    Args:
        image (np.ndarray): 3-D array of image data.
        mask (np.ndarray): 3-D array of mask data.
        window_size (int): size of the sliding window for noise calculation.
            Defaults to 8.
    Returns:
        Tuple of SNR and Rayleigh SNR and image noise
    """
    shape = np.shape(image)
    # dilate the mask to analyze noise area away from the signal
    kernel_shape = (
        _get_dilation_kernel(shape[0]),
        _get_dilation_kernel(shape[1]),
        _get_dilation_kernel(shape[2]),
    )
    dilate_struct = np.ones((kernel_shape))
    noise_mask = binary_dilation(mask, dilate_struct).astype(bool)

    noise_temp = np.copy(image)
    noise_temp[noise_mask] = np.nan
    # set up for using mini noise cubes through the image and calculate std for noise
    n_noise_vox = window_size * window_size * window_size
    mini_vox_std = 0.75 * n_noise_vox  # minimul number of voxels to calculate std

    stepper = 0
    total = 0
    std_dev_mini_noise_vol = []

    for ii in range(0, int(shape[0] / window_size)):
        for jj in range(0, int(shape[1] / window_size)):
            for kk in range(0, int(shape[2] / window_size)):
                print(ii, jj, kk)
                mini_cube_noise_dist = noise_temp[
                    ii * window_size : (ii + 1) * window_size,
                    jj * window_size : (jj + 1) * window_size,
                    kk * window_size : (kk + 1) * window_size,
                ]
                mini_cube_noise_dist = mini_cube_noise_dist[
                    ~np.isnan(mini_cube_noise_dist)
                ]
                # only calculate std for the noise when it is long enough
                if len(mini_cube_noise_dist) > mini_vox_std:
                    std_dev_mini_noise_vol.append(np.std(mini_cube_noise_dist, ddof=1))
                    stepper = stepper + 1
                total = total + 1

    image_noise = np.median(std_dev_mini_noise_vol)
    image_signal = np.average(image[mask])

    SNR = image_signal / image_noise
    return SNR, SNR * 0.66, image_noise


def inflation_volume(mask: np.ndarray, fov: float) -> float:
    print("Computing inflation volume")
    """Calculate the inflation volume of isotropic 3D image.

    Args:
        mask: np.ndarray thoracic cavity mask.
        fov: float field of view in cm
    Returns:
        Inflation volume in L.
    """
    return (
        np.sum(mask) * fov**3 / np.shape(mask)[0] ** 3
    ) / constants.FOVINFLATIONSCALE3D


def process_date() -> str:
    """Return the current date in YYYY-MM-DD format."""
    now = datetime.now()
    return now.strftime("%Y-%m-%d")


def bin_percentage(image: np.ndarray, bins: np.ndarray, mask: np.ndarray) -> float:
    print("computing bin_percentage")
    """Get the percentage of voxels in the given bins.

    Args:
        image: np.ndarray binned image. Assumes that the values in the image are
            integers representing the bin number. Bin 0 is the region outside the mask
            and Bin 1 is the lowest bin, etc.
        bins: np.ndarray list of bins to include in the percentage calculation.
        mask: np.ndarray mask of the region of interest.
    Returns:
        Percentage of voxels in the given bins.
        
    Haad: 
    np.isin(some_elements, other_elements) checks if each element in element is present in test_elements. 
    
    some_elements and other_elements are both array-like objects.
    
    some_elements is the underlying 3D data matrix of the binned image,
    whereas other_elements is a list of discrete pixel intensities (bins) that we want to check against.
    
    As an example, if test_elements is the list [1,2,3], and some_elements 
    has an entry that is 3, then the corresponding voxel (which has the pixel intensity of 3), will be included in the count of voxels that fall into the bins (i.e. the quantity called volume_in_bins).
    """

    dask_image = da.from_array(image, chunks=(512, 512, 50))
    dask_mask = da.from_array(mask, chunks=(512, 512, 50))
    dask_bins = da.from_array(bins, chunks="auto")

    # return 100 * np.sum(np.isin(image, bins)) / np.sum(mask > 0)

    mask_volume = da.sum(dask_mask > 0) # dask_mask_sum
    volume_in_bins = da.sum(da.isin(dask_image, dask_bins)) 
    print(f"bin_percentage(): volume_in_bins = {volume_in_bins.compute()}")
    print(f"bin_percentage(): mask_volume = {mask_volume.compute()}")
    
    """
    Haad:
    We should check if dask_mask_sum is really big or really small.
    
    Right now (June 16th, 2025), membrane_defect_pct is all zero so 
    """
    # if dask_mask_sum == 0:
    if math.isclose(mask_volume, 0):
        raise ValueError(
            "Haad: da.sum(dask_mask) is very small, bin percentage may be very large!"
        )
    # elif math.isclose(dask_mask_sum, float("inf")):
    #     raise ValueError(
    #         "Haad: da.sum(dask_mask) is very large, bin percentage may be very small!"
    #     )

    res = 100 * volume_in_bins / mask_volume
  
    res_computed = res.compute()
    if res_computed > 100:
        print("Haad: Warning, computed bin percentage greater than 100%.")
    
    # return res.compute()
    return res_computed

def mean(image: np.ndarray, mask: np.ndarray) -> float:
    print("computing mean")
    """Get the mean of the image.

    Args:
        image: np.ndarray. The image.
        mask: np.ndarray. mask of the region of interest.()
    Returns:
        Mean of the image.
    """

    print(f"mean(): image.shape = {image.shape}")
    print(f"mean(): mask.shape = {mask.shape}")

    if image.shape != mask.shape:
        raise ValueError("image and mask must have the same shape")

    if not mask.any():
        raise ValueError("The mask is empty. No region to compute the mean.")

    if np.isnan(image).any() or np.isinf(image).any():
        raise ValueError("The input image contains NaN or Inf values.")

    #    if image.shape != mask.shape:
    #        raise ValueError("image and mask must have the same shape")

    mask = mask.astype(bool)
    dask_image = da.from_array(image, chunks=(512, 512, 50))
    dask_mask = da.from_array(mask, chunks=(512, 512, 50))

    res = da.mean(dask_image[dask_mask])
    res_computed = res.compute()

    print(f"Computed mean: {res_computed}")
    if np.isnan(res_computed):
        raise ValueError("Computed result in mean is NaN")

    return res_computed  # return np.mean(np.multiply(image, mask))


def negative_percentage(image: np.ndarray, mask: np.ndarray) -> float:
    print("computing negative percentage")
    """Get the percentage voxels of image inside mask that are negative.

    Args:
        image: np.ndarray. The image.
        mask: np.ndarray. mask of the region of interest.
    Returns:
        Percentage of voxels in the image that are negative.
    """
    return 100 * np.sum(image[mask] < 0) / np.sum(mask)


def median(image: np.ndarray, mask: np.ndarray) -> float:
    print("computing median")
    """Get the median of the image.

    Args:
        image: np.ndarray. The image.
        mask: np.ndarray. mask of the region of interest.
    Returns:
        Median of the image.
    """
    return np.median(image[mask])


def std(image: np.ndarray, mask: np.ndarray) -> float:
    print("computing std")
    """Get the standard deviation of the image.

    Args:
        image: np.ndarray. The image.
        mask: np.ndarray. mask of the region of interest.
    Returns:
        Standard deviation of the image.
    """
    return np.std(image[mask])


def dlco(
    image_gas: np.ndarray,
    image_membrane: np.ndarray,
    image_rbc: np.ndarray,
    mask: np.ndarray,
    mask_vent: np.ndarray,
    fov: float,
    membrane_mean: float = 0.736,
    rbc_mean: float = 0.471,
) -> float:
    print("computing dlco")
    """Get the DLCO of the image.

    Reference: https://journals.physiology.org/doi/epdf/10.1152/japplphysiol.00702.2020
    Args:
        image_gas: np.ndarray. The ventilation image.
        image_membrane: np.ndarray. The membrane image.
        img_rbc: np.ndarray. The RBC image.
        mask: np.ndarray. thoracic cavity mask.
        mask_vent: np.ndarray. mask of the non-VDP region.
        fov: float. field of view in cm.
        membrane_mean: float. The mean membrane in healthy subjects.
        rbc_mean: float. The mean RBC in healthy subjects.
    """
    return kco(
        image_membrane, image_rbc, mask_vent, membrane_mean, rbc_mean
    ) * alveolar_volume(image_gas, mask, fov)


def alveolar_volume(image: np.ndarray, mask: np.ndarray, fov: float) -> float:
    print("computing alveolar volume")
    """Get the alveolar volume of the image.

    Reference: https://journals.physiology.org/doi/epdf/10.1152/japplphysiol.00702.2020
    Args:
        image: np.ndarray. The binned ventilation image.
        mask: np.ndarray. thoracic cavity mask.
        fov: float. field of view in cm.
    Returns:
        Alveolar volume in L.
    """
    return (
        constants.VA_ALPHA
        * inflation_volume(mask, fov)
        * (1.0 - bin_percentage(image, np.asarray([1]), mask) / 100)
    )


def kco(
    image_membrane: np.ndarray,
    image_rbc: np.ndarray,
    mask: np.ndarray,
    membrane_mean: float = 0.736,
    rbc_mean: float = 0.471,
) -> float:
    """Get the KCO of the image.

    Reference: https://journals.physiology.org/doi/epdf/10.1152/japplphysiol.00702.2020
    Args:
        image_membrane: np.ndarray. The membrane image.
        img_rbc: np.ndarray. The RBC image.
        mask: np.ndarray. mask of non-VDP region.
        membrane_mean: float. The mean membrane in healthy subjects.
        rbc_mean: float. The mean RBC in healthy subjects.
    """
    membrane_rel = mean(image_membrane, mask) / membrane_mean
    rbc_rel = mean(image_rbc, mask) / rbc_mean
    membrane_rel = 1.0 / membrane_rel if membrane_rel > 1 else membrane_rel
    return 1 / (
        1 / (constants.KCO_ALPHA * membrane_rel) + 1 / (constants.KCO_BETA * rbc_rel)
    )


def rdp_ba(
    image_rbc_binned: np.ndarray,
    mask: np.ndarray,
) -> float:
    """
    Compute the RBC defect bias from apical (top) to basilar (bottom) regions across both lungs.

    This metric (ΔRDP_BA) is designed to quantify how RBC defects are distributed spatially 
    from the top to the bottom of the lungs using binarized RBC images (bin 1 or 2 indicates RBC defect).
    It focuses only on the middle 40%-80% of valid axial slices to avoid extreme slices with noisy segmentation.

    Args:
        image_rbc_binned (np.ndarray): 3D array (height x width x slices) where voxel values are binned RBC signal.
                                       Bin 1 and 2 represent RBC defects.
        mask (np.ndarray): 3D binary mask (same shape as image_rbc_binned) defining the lung region of interest.

    Returns:
        float: ΔRDP_BA value — a scalar representing the RBC defect bias towards the basilar region.
               Positive values indicate higher RBC defect in the lower lung; negative indicates upper bias.
    """
    data_images = image_rbc_binned

    # number of split 
    ns = 3
    valid_slices = []  # Store indices where mask is non-zero
    total_mean=[]

    # Loop over each slice (assuming 128 slices)
    for ij in range(128):
        bar2gas_current = ndimage.rotate(image_rbc_binned[:, :, ij], 0)
        mask_current = ndimage.rotate(mask[:, :, ij], 0)

        if np.sum(mask_current) > 0:
            valid_slices.append(ij)
    if len(valid_slices) > 0:
        start_idx = int(len(valid_slices) * 0.4)  # Get 40% index (integer part)
        end_idx = int(len(valid_slices) * 0.8)    # Get 80% index (integer part)

        selected_slices = valid_slices[start_idx:end_idx]  # Extract the range

    for ij in selected_slices:
        bar2gas_current = ndimage.rotate(image_rbc_binned[:, :, ij], 0)
        mask_current = ndimage.rotate(mask[:, :, ij], 0)

        mask_current = mask_current.astype(np.uint8)
        
        output=cv2.connectedComponentsWithStats(mask_current,4)

        num_labels = output[0]
        labels_im = output[1]
        stats=output[2]
        centroid=output[3]

        if(num_labels<=2):
            continue

        area=stats[:,4]
        # Delete the background label.
        area=area[1:]

        # Choose the label with largest and second largest except background
        index_label=np.array(heapq.nlargest(2, range(len(area)), key=area.__getitem__))+1

        # Find which is left or right
        index_1 = index_label[0]
        index_2 = index_label[1]
        if (centroid[index_1,0]<centroid[index_2,0]):
            left_label=index_1
            right_label=index_2
        else:
            left_label=index_2
            right_label=index_1

        top_left= stats[left_label,1]
        height_left = stats[left_label,3]

        top_right= stats[right_label,1]
        height_right = stats[right_label,3]

        [m,n] = mask_current.shape
        # Initialize sum_all and num_all correctly
        sum_all = np.zeros(ns * 2)
        num_all = np.zeros(ns * 2)

        # Create ns equally spaced intervals for splitting
        split_indices_left = np.linspace(top_left, top_left + height_left, ns+1, dtype=int)
        split_indices_right = np.linspace(top_right, top_right + height_right, ns+1, dtype=int)

        for i in range(m):
            for j in range(n):
                if labels_im[i, j] == left_label:
                    for nlf in range(ns):
                        lower_l_left, upper_l_left = split_indices_left[nlf], split_indices_left[nlf+1]
                        if lower_l_left <= i < upper_l_left:
                            if data_images[i, j, ij] in [1,2]:
                                num_all[nlf] += data_images[i, j, ij]
                            sum_all[nlf] += data_images[i, j, ij]

                elif labels_im[i, j] == right_label:
                    for nlf in range(ns):
                        lower_l_right, upper_l_right = split_indices_right[nlf], split_indices_right[nlf+1]
                        if lower_l_right <= i < upper_l_right:
                            if data_images[i, j, ij] in [1,2]:
                                num_all[nlf + ns] += data_images[i, j, ij]
                            sum_all[nlf + ns] += data_images[i, j, ij]

        mean=[]
        for nlf in range(ns * 2):
            if(sum_all[nlf]!=0):
                mean.append(num_all[nlf]/sum_all[nlf])
            else:
                mean.append(np.nan)

        total_mean.append(mean)
    total_mean=np.array(total_mean)
    total_mean=np.nanmean(total_mean,axis=0)

    bottom = total_mean[2]+total_mean[5]
    top = total_mean[0]+total_mean[1]+total_mean[3]+total_mean[4]
    b_t = (bottom - top/2) / 2 * 100
    return b_t