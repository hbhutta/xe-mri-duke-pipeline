import ants
from multiprocessing import Pool
from __future__ import division
from datetime import datetime
import os

imgs = [ 
    ants.image_read("tmp/image_membrane2gas_binned.nii"),
    ants.image_read("tmp/image_rbc2gas_binned.nii"),
    ants.image_read("tmp/image_rbc2gas.nii"),
    ants.image_read("tmp/image_membrane2gas.nii"),
    ants.image_read("tmp/image_gas_cor.nii"),
    ants.image_read("tmp/mask.nii"),
    ants.image_read("tmp/mask_vent.nii")
] 

def apply_transforms(target) -> None:
    """Applies the forward transforms from the transformlist 
    to the target. Saves a new file for the warped target, 
    leaving the original target intact for later use.
   
    We can optionally delete the generated warped targets 
    once we have computed the statistics.
    
    But we may also want to keep them for testing purposes.
    
    Uses the binary 'antsApplyTransforms'
    
    Args:
    target (): A nifti image
    transformlist: A list of transform file paths
    """
    cmd = ''
    os.system(cmd)
    
    pass


def main():
    with Pool() as p:
        p.map(apply_transforms, imgs)

if __name__ == '__main__':
    start_time = datetime.now()
    main()
    end_time = datetime.now()
    elapsed_time = ((end_time - start_time).total_seconds() / 60.0)
    print(f"That took {elapsed_time} minutes")
