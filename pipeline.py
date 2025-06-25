import os
import csv

def get_ratio(patient: str):
    with open("cohort_rbc_mem_ratios.csv", 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if patient in row:
                return row[1]

for patient in os.listdir("cohort"):
    print(f"\n\n\n\nprocessing patient {patient}\n\n\n\n")
    patient_path = os.path.join("cohort", patient)
   
    manual_seg_filepath = f"{patient_path}/mask_reg_edited.nii"
    os.system(f"python reconstruct.py --config config/tests/cohort_master_config.py --patient_path {patient_path} --rbc_m_ratio {get_ratio(patient)} --manual_seg_filepath {manual_seg_filepath} --force_recon")
    os.system(f"python reorient.py")
    os.system(f"bash mod_corepeel.sh {patient_path}")
    os.system(f"python resize.py")
    os.system(f"python register.py")
    os.system(f"python unpack.py")
    os.system(f"python warp_vent.py {patient}")
    os.system(f"python stats.py --config config/tests/cohort_master_config.py --patient_path {patient_path}")
    os.system(f"bash clean.sh {patient_path}")



#python reconstruct.py --config config/tests/cohort_master_config.py --force_recon 
#python reorient.py $dir
#bash mod_corepeel.sh $dir
#python resize.py
#python register.py
#python unpack.py
#python warp_vent.py
#python stats.py --config config/tests/cohort_master_config.py
#bash clean.sh # clean files no longer needed in this dir to save space
#
#

