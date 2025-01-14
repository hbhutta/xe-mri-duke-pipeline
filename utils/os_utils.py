import os
import glob
from nibabel.orientations import aff2axcodes 

"""
Return the oritentation info for a NIFTI (Neuroimaging Informatics Technology Initiative) file

This information includes:
1. Quaternion-based rotation (quatern_b, quatern_c, quatern_d)
2. Translation (qoffset_x, qoffset_y, qoffset_z)
3. Scaling factors for affine transformations (srow_x, srow_y, srow_z)


References:
https://nifti.nimh.nih.gov/nifti-1/documentation/nifti1fields/nifti1fields_pages/quatern.html

"""


"""
Given a directory, list the files common to all the first-level subdirectories
"""


def get_common_files(base_dir: str, filename: str | None) -> list[str]:
    file_sets_by_subdir = {}
    sample_subdir = None
    for subdir in os.listdir(base_dir):
        sample_subdir = subdir
        subdir_path = os.path.join(base_dir, subdir)
        files = [file for file in os.listdir(subdir_path)]
        file_sets_by_subdir[subdir] = set(files)

    common_files = file_sets_by_subdir[sample_subdir]
    for key in file_sets_by_subdir.keys():
        common_files &= file_sets_by_subdir[key]

    common_files = list(common_files)
    all_file_paths = glob.glob('**/*', root_dir=base_dir)
    common_file_paths = [file_path for file_path in all_file_paths if any(
        common_file in file_path for common_file in common_files)]
    
    ret = [os.path.join(base_dir, file_path) for file_path in common_file_paths]
    
    if filename:
       return list(filter(lambda x: filename in x, ret))
    return ret


# """
# Returns the specified .nii common to all patients in the specified directory
# """
# def get_common_nii(dir: str, filename: str) -> list[NII] | list:
#     common_file_paths = get_common_files(base_dir=dir)
#     nii_files = list(filter(lambda x: filename in x, common_file_paths))
#     return nii_files


# def read_ANTS(as_type: str, dir: str, ct_filename="", mr_filename="", vent_filename="") -> list:
#     try:
#         assert as_type in ['ct', 'proton', 'vent']
#     except AssertionError as e:
#         print("as_type must be either ct, proton or vent")
# # 
#     common_file_paths = get_common_files(base_dir=dir)
#     # print(common_file_paths)
#     match as_type:
#         case 'ct':
#             file_name = ct_filename
#         case "proton":
#             file_name = mr_filename
#         case "vent":
#             file_name = vent_filename
#     nii_files = list(filter(lambda x: file_name in x, common_file_paths))
#     # print(nii_files)
#     return nii_files


"""
Given a path to a CT .nii file and a proton (MRI) .nii file,
make the orientation of the MRI file the same as the orientation
of the CT file.

This is done by using the applying the orientation matrix
of the CT image derived from its affine matrix to the
numpy matrix representing the original proton (MRI) image

The newly oriented image is saved to file with the original filename
and the new axcodes appended to it.

The new NII object is also returned for further use in a pipeline
"""


# def orient_img(img: NII, new_axcodes: tuple, ret: bool) -> NII | None:
#     print(f"axcodes before:\n {img.get_axcodes()}")
#     print(f"affine before:\n {img.get_affine()}")

#     old_ornt = axcodes2ornt_RAS(axcodes=img.get_axcodes())
#     new_ornt = axcodes2ornt_RAS(axcodes=new_axcodes)
#     ornt_trans = ornt_transform(start_ornt=old_ornt, end_ornt=new_ornt)

#     oriented_dataobj = apply_orientation(
#         arr=np.array(img.get_matrix()), ornt=ornt_trans)

#     new_affine = img.get_affine().dot(
#         inv_ornt_aff(ornt=ornt_trans, shape=img.get_shape()))

#     img_oriented_ni = nib.Nifti1Image(
#         dataobj=oriented_dataobj, affine=new_affine)

#     img_ni_oriented_filename = os.path.dirname(img.filename) + '/' + \
#         f'{os.path.basename(img.filename)[:-len(".nii")]}_{axcode_to_str(
#             axcode_to_str(aff2axcodes(new_affine)))}.nii'

#     nib.save(img=img_oriented_ni, filename=img_ni_oriented_filename)
#     print(f"Saved to filename: {img_ni_oriented_filename}")

#     img_oriented = NII(nii_filename=img_ni_oriented_filename)

#     print(f"axcodes after:\n {img_oriented.get_axcodes()}")
#     print(f"affine before:\n {img_oriented.get_affine()}")

#     if ret:
#         return img_oriented


# """
# Serializes the result of a registration using pickle
# """


# def save_reg(prefix: str, reg) -> None:
#     save_name = prefix + "_reg.pkl"
#     with open(save_name, "wb") as file:
#         pickle.dump(reg, file)
#         print(f"Serialized registration to {save_name}: {reg}")


# """
# Loads the pickled registration 
# """


# def load_reg(save_name: str):
#     with open(save_name, "rb") as file:
#         reg = pickle.load(file)[0]
#         assert type(reg) == dict
#         print(f"Loaded registration from {save_name}")
#     return reg


# """
# Converts axcodes to strings 
# """


# def axcode_to_str(axcodes: tuple) -> str:
#     return ''.join(axcodes)


# """
# Using RAS coding instead of LPI coding to create orientation matrices
# """


# def axcodes2ornt_RAS(axcodes):
#     # R -> L, A -> P, S -> I
#     return axcodes2ornt(axcodes=axcodes, labels=(('R', 'L'), ('P', 'A'), ('S', 'I')))


def aff2axcodes_RAS(aff):
    """Print RAS axcodes given an affine
   
    Args:
        aff (np.ndarray): affine
    """
    return aff2axcodes(aff=aff, labels=(('R', 'L'), ('A', 'S'), ('S', 'I')))


#"""
#Return the paths to the subdirs of a given dir
#"""
#
#
#def get_subdirs(dir: str) -> list[str]:
#    return [os.path.join(dir, subdir) for subdir in os.listdir(dir)]
# 
# 
# def get_affine(nii_filepath: str) -> list:
    # nib_ = nib.load(nii_filepath)
    # hdr = nib_.header
    # srow_x = hdr['srow_x']
    # srow_y = hdr['srow_y']
    # srow_z = hdr['srow_z']
    # return np.array([srow_x, srow_y, srow_z])
# 
# 
# def nib_save(nib_img, path: str):
    # if not os.path.exists(path):
        # nib.save(img=nib_img, filename=path)
        # print(f"Saved to {path}!")
        # print(aff2axcodes_RAS(nib_img.affine))
    # else:
        # print(f"File {path} already exists.")
