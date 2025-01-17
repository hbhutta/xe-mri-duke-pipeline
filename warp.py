"""Scripts to run gas exchange mapping pipeline."""

#from absl import flags
#from absl.flags import FLAGS
#import sys
import os 
from multiprocessing import Pool
from datetime import datetime
import ants
import pickle 
import nibabel as nib
from nibabel.nifti1 import Nifti1Image
from reorient import reorient_mr

#flags.DEFINE_string(name="data_dir",
#                    default=None, # assuming that this is where .dat files are stored by default
#                    help="The folder where the .dat files are stored",
#                    required=True)

data_dir = "cohort/PIm0015"

def warp_image(moving):
    '''
    Use transforms from registration process to warp an image to target.  For example, if you register the ventilation mask to the CT mask,
    you can use the transforms to warp the ventilation intensity image to the CT space.    

    Parameters
    ----------
    moving : str
        path to fixed image defining domain into which the moving image is transformed
    fixed : str
        path to target image.
    transform_list : list
        list of transforms ***in following order*** [1Warp.nii.gz,0GenericAffine.mat] 
    interpolation : str
            linear (default)
            nearestNeighbor
            multiLabel for label images but genericlabel is preferred
            gaussian
            bSpline
            cosineWindowedSinc
            welchWindowedSinc
            hammingWindowedSinc
            lanczosWindowedSinc
            genericLabel use this for label images

    Returns
    -------
    image warped to target image.
    '''
    
    
   
    ct_mask = ants.image_read(f"{data_dir}/CT_mask.nii")
    with open(f"{data_dir}/{os.path.basename(data_dir)}_reg.pkl", "rb") as file:
        mytx = pickle.load(file)

    print(len(mytx['fwdtransforms']))
  
#    nib_moving = nib.load(moving)
    # Try to resolve unexpected scales in sform
#    px = nib_moving.header['pixdim'][1]
#    py = nib_moving.header['pixdim'][2]
#    pz = nib_moving.header['pixdim'][3]
#
#    nib_moving.header['srow_x'] = [px, 0, 0, 1]
#    nib_moving.header['srow_y'] = [0, py, 0, 1]
#    nib_moving.header['srow_z'] = [0, 0, pz, 1]
#    new_nib_moving = Nifti1Image(nib_moving.get_fdata(), affine=nib_moving.affine, header=nib_moving.header)
    
    # Overwrite existing image
    #nib.save(img=new_nib_moving, filename=nib_moving.get_filename()[:-4] + "_srow_fixed.nii")
    
    # Check header
    #print(nib_moving.header)
    
    reorient_mr(moving)
    new_moving = moving[:-4] + "_mutated_affine.nii"
    if (os.path.isfile(new_moving)):
        ants_moving = ants.image_read(new_moving)
    else:
        raise FileNotFoundError

    trans = ants.apply_transforms(fixed=ct_mask,
                                  moving=ants_moving,
                                  transformlist=mytx['fwdtransforms'],
                                  interpolator='linear',
                                  imagetype=0,
                                  whichtoinvert=None,
                                  defaultvalue=0, verbose=True)
    
    assert trans != None
    
    ants.image_write(image=trans, filename=new_moving)


def main():
    imgs = [ 
        f"{data_dir}/image_membrane2gas_binned.nii",
        f"{data_dir}/image_rbc2gas_binned.nii",
        f"{data_dir}/image_rbc2gas.nii",
        f"{data_dir}/image_membrane2gas.nii",
        f"{data_dir}/image_gas_cor.nii",
        # f"{data_dir}/mask.nii",
        f"{data_dir}/mask_vent.nii",
        f"{data_dir}/image_gas_binned.nii",
        f"{data_dir}/image_gas_highreso.nii"
    ]

    for img in imgs:
        reorient_mr(img) 
        
#    with Pool() as pool:
#        pool.starmap(warp_image, imgs)
    
if __name__ == '__main__':
#    start = datetime.now()
    main()
#    end = datetime.now()
#    elapsed = (end - start).seconds / 60
#    print(f"That took {elapsed} minutes")
