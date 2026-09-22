"""
data_loader.py
----------------
Loading and cleaning the dataset before part 1 of the analysis
"""

import pandas as pd

ALGO_NAMES = ["algo1", "algo2", "algo3"]
AGE_BINS = [0, 18, 30, 40, 50, 60, 70, 80, 130]
AGE_LABELS = ["0-18", "18-30", "30-40", "40-50", "50-60", "60-70", "70-80", "80+"]

TIMESTAMP_COLS = [
    "scan_timestamp", "radiologist_sign_time", "algos_start_run",
    "algo1_finish_run", "algo2_finish_run", "algo3_finish_run",
]

#loading the data
def load_raw(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.drop(columns=[c for c in df.columns if c.startswith("Unnamed")], errors="ignore")

    for col in TIMESTAMP_COLS:            #csv has no dtype info, so timestamps load as plain
        if col in df.columns:             #strings unless we parse them explicitly. format="mixed"
            df[col] = pd.to_datetime(df[col], format="mixed")   #handles rows with inconsistent date formats

    return df

#creating derived fields for analysis
def add_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    df["duration_min"] = (df["radiologist_sign_time"] - df["scan_timestamp"]).dt.total_seconds() / 60       #minutes from scan acquisition to radiologist sign-off   
    df["start_delay_s"] = (df["algos_start_run"] - df["scan_timestamp"]).dt.total_seconds()         #seconds from scan acquisition to algorithms starting to run

    for algo in ALGO_NAMES:         #seconds each algorithm took to run
        df[f"{algo}_runtime_s"] = (
            df[f"{algo}_finish_run"] - df["algos_start_run"]
        ).dt.total_seconds()                 

    df["is_ed"] = df["patient_class"].eq("ED")      #was the patient in Emergency Department
    df["rad_positive"] = df["radiologist_answer"].eq("P")       #did the radiologist call the scan positive
    df["age_group"] = pd.cut(df["age"], bins=AGE_BINS, labels=AGE_LABELS, right=False)   #age bracket, for age-stratified prevalence checks

    df["scan_hour"] = df["scan_timestamp"].dt.hour
    df["scan_dow"] = df["scan_timestamp"].dt.day_name()         #day-of-week the scan was taken
    df["scan_month"] = df["scan_timestamp"].dt.to_period("M").astype(str)

    return df

#creating a summary of data-quality issues
def data_quality_report(df: pd.DataFrame) -> dict:

    report = {}

    #missing values per column
    report["missing_values"] = df.isna().sum()
    report["missing_values"] = report["missing_values"][report["missing_values"] > 0]   #only keeping the missing values

    #empty values per column
    report["empty_string_values"] = (df.astype(str).apply(lambda col: col.str.strip() == "")).sum()
    report["empty_string_values"] = report["empty_string_values"][report["empty_string_values"] > 0]

    #duplicated accession numbers
    dup_mask = df["accession"].notna() & df["accession"].duplicated(keep=False)
    report["duplicated_accessions"] = df.loc[dup_mask, ["accession", "site", "scan_timestamp"]]

    #negative radiologist scan durations
    dur = (df["radiologist_sign_time"] - df["scan_timestamp"]).dt.total_seconds() / 60
    report["negative_duration_rows"] = df.loc[dur < 0]

    #scans where algorithms started before the scan was even taken
    start_delay = (df["algos_start_run"] - df["scan_timestamp"]).dt.total_seconds()
    report["negative_start_delay_rows"] = df.loc[start_delay < 0]

    #negative algorithm runtimes
    for algo in ALGO_NAMES:
        rt = (df[f"{algo}_finish_run"] - df["algos_start_run"]).dt.total_seconds()
        report[f"negative_{algo}_runtime_rows"] = df.loc[rt < 0]

    return report

#creating a wrapper for the previous functions
def load_and_prepare(path: str) -> tuple[pd.DataFrame, dict]:
    raw = load_raw(path)
    df = add_derived_fields(raw)
    quality = data_quality_report(raw)
    return df, quality