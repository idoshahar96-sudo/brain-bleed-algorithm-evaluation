"""
exploration.py
----------------
Part 1 of the analysis: data exploration
"""

import pandas as pd

#population demographics break down
def population_summary_by(df: pd.DataFrame, group_cols) -> pd.DataFrame:
    if isinstance(group_cols, str):
        group_cols = [group_cols]
    total_n = len(df)
    out = df.groupby(group_cols).agg(
        n_scans=("accession", "count"),
        pct_male=("gender", lambda s: (s == "male").mean()),
        mean_age=("age", "mean"),
        median_age=("age", "median"),
    ).round(3)
    out.insert(1, "pct_of_total", (out["n_scans"] / total_n * 100).round(2))
    out.insert(3, "pct_female", (1 - out["pct_male"]).round(3))
    return out


#summarizing scan to sign-off duration
def duration_summary(df: pd.DataFrame, group_cols=None) -> pd.DataFrame:
    if group_cols is None:
        s = df["duration_min"].describe()
        return s.to_frame(name="duration_min")

    total_n = len(df)
    summary = df.groupby(group_cols)["duration_min"].describe()[["count", "mean", "std", "min", "50%", "max"]]
    summary.insert(0, "pct_of_total", (summary["count"] / total_n * 100).round(1))
    return summary


#ICH-positive rate per group
def prevalence_by(df: pd.DataFrame, group_cols) -> pd.DataFrame:
    return df.groupby(group_cols, observed=True)["rad_positive"].agg(["mean", "count"]).rename(
        columns={"mean": "ich_prevalence", "count": "n"}
    )

#crating a pivot table of scan volume by hour-of-day x day-of-week
def volume_by_hour_dow(df: pd.DataFrame) -> pd.DataFrame:
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = df.pivot_table(index="scan_hour", columns="scan_dow", values="accession", aggfunc="count", fill_value=0)
    pivot = pivot.reindex(columns=[d for d in order if d in pivot.columns])
    return pivot

def monthly_volume(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("scan_month")["accession"].count().rename("n_scans")