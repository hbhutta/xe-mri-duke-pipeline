import os
import pandas as pd

df = pd.read_csv('csvs/cohort_rbc_mem_ratios.csv')
pims = df['PIm'].tolist()
pims_with_missing_ratio = [patient for patient in os.listdir("cohort") if patient not in pims]
pims_with_missing_ratio.sort()
for p in pims_with_missing_ratio:
    print(p)