import os
import csv
from tqdm import tqdm

def get_ratio(patient: str):
    with open("cohort_rbc_mem_ratios.csv", 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if patient in row:
                return row[1]

# List all patients in the cohort
patients = os.listdir("cohort")

# Iterate over patients with a progress bar
for patient in tqdm(patients, desc="Processing Patients", unit="patient"):
    print(f"\n\n\n\nProcessing patient {patient}\n\n\n\n")
    patient_path = os.path.join("cohort", patient)

    manual_seg_filepath = f"{patient_path}/mask_reg_edited.nii"
    
    # Define tasks for the pipeline
    tasks = [
        (f"python reconstruct.py --config config/tests/cohort_master_config.py --patient_path {patient_path} "
         f"--rbc_m_ratio {get_ratio(patient)} --manual_seg_filepath {manual_seg_filepath} --force_recon", "Reconstruct"),
        ("python reorient.py", "Reorient"),
        (f"bash mod_corepeel.sh {patient_path}", "Core Peel"),
        ("python resize.py", "Resize"),
        ("python register.py", "Register"),
        ("python unpack.py", "Unpack"),
        (f"python warp_vent.py {patient}", "Warp Vent"),
        (f"python stats.py --config config/tests/cohort_master_config.py --patient_path {patient_path}", "Stats"),
        (f"bash clean.sh {patient_path}", "Clean"),
    ]
    
    # Run each task with its own progress bar
    for command, description in tqdm(tasks, desc=f"Patient {patient}", unit="task"):
        os.system(command)