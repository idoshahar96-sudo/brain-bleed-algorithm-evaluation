"""
performance.py
----------------
Part 2 of the analysis: algorithm performance evaluation
"""

import numpy as np
import pandas as pd

ALGO_NAMES = ["algo1", "algo2", "algo3"]

#confusion-matrix counts for a P/N prediction series against the ground truth
def confusion_counts_from_answers(df: pd.DataFrame, pred: pd.Series) -> dict:
    gt = df["radiologist_answer"]
    tp = int(((gt == "P") & (pred == "P")).sum())
    fn = int(((gt == "P") & (pred == "N")).sum())
    fp = int(((gt == "N") & (pred == "P")).sum())
    tn = int(((gt == "N") & (pred == "N")).sum())
    return {"TP": tp, "FN": fn, "FP": fp, "TN": tn}


#creating a confusion-matrix for one of the algoX_answer columns
def confusion_counts(df: pd.DataFrame, algo: str) -> dict:
    return confusion_counts_from_answers(df, df[f"{algo}_answer"])


#formatting confusion-matrix for the visualization
def format_confusion_counts(counts: dict) -> dict:
    tp, fn = counts["TP"], counts["FN"]
    fp, tn = counts["FP"], counts["TN"]

    pos_row_total = tp + fn
    neg_row_total = fp + tn

    def fmt(value, row_total):
        pct = (value / row_total * 100) if row_total > 0 else 0.0
        return f"{value:,}\n({pct:.1f}%)"

    return {
        "TP": fmt(tp, pos_row_total),
        "FN": fmt(fn, pos_row_total),
        "FP": fmt(fp, neg_row_total),
        "TN": fmt(tn, neg_row_total),
    }


#calculating standard classification metrics
def metrics_from_counts(c: dict) -> dict:
    tp, fn, fp, tn = c["TP"], c["FN"], c["FP"], c["TN"]
    n = tp + fn + fp + tn
    sens = tp / (tp + fn) if (tp + fn) else np.nan       # recall / sensitivity
    spec = tn / (tn + fp) if (tn + fp) else np.nan
    ppv = tp / (tp + fp) if (tp + fp) else np.nan          # precision
    npv = tn / (tn + fn) if (tn + fn) else np.nan
    acc = (tp + tn) / n if n else np.nan
    f1 = 2 * ppv * sens / (ppv + sens) if (ppv and sens and (ppv + sens)) else np.nan
    return {
        "n": n, "sensitivity": sens, "specificity": spec,
        "PPV": ppv, "NPV": npv, "accuracy": acc, "F1": f1,
    }


#combining confusion-matrix and metrics into one table
def algo_performance_table(df: pd.DataFrame, algos=ALGO_NAMES) -> pd.DataFrame:
    rows = {}
    for algo in algos:
        c = confusion_counts(df, algo)
        m = metrics_from_counts(c)
        rows[algo] = {**c, **m}
    return pd.DataFrame(rows).T.round(3)


#calculating metrics per subset
def algo_performance_by_group(df: pd.DataFrame, group_cols, algos=ALGO_NAMES) -> pd.DataFrame:
    if isinstance(group_cols, str):
        group_cols = [group_cols]
    out = []
    for grp, sub in df.groupby(group_cols):
        if not isinstance(grp, tuple):
            grp = (grp,)
        row = dict(zip(group_cols, grp))
        for algo in algos:
            c = confusion_counts(sub, algo)
            m = metrics_from_counts(c)
            out.append({**row, "algo": algo, **m})
    return pd.DataFrame(out).round(3)


#percent-agreement matrix between algorithms
def pairwise_agreement(df: pd.DataFrame, algos=ALGO_NAMES) -> pd.DataFrame:
    mat = pd.DataFrame(index=algos, columns=algos, dtype=float)
    for a in algos:
        for b in algos:
            mat.loc[a, b] = (df[f"{a}_answer"] == df[f"{b}_answer"]).mean()
    return mat.round(3)


#algorithm runtime summary stats
def runtime_summary(df: pd.DataFrame, algos=ALGO_NAMES) -> pd.DataFrame:
    cols = [f"{a}_runtime_s" for a in algos]
    return df[cols].describe().T[["mean", "std", "min", "50%", "max"]].round(2)


#combines two algorithms predictions with OR or AND
def ensemble_answer(df: pd.DataFrame, algo_a: str, algo_b: str, mode: str = "or") -> pd.Series:
    a = df[f"{algo_a}_answer"] == "P"
    b = df[f"{algo_b}_answer"] == "P"
    positive = (a | b) if mode == "or" else (a & b)
    return positive.map({True: "P", False: "N"})


#builds a metrics table that includes OR/AND ensembles of two algorithms
def algo_performance_table_with_ensembles(df: pd.DataFrame, algo_a: str, algo_b: str,
                                           algos=ALGO_NAMES) -> pd.DataFrame:
    base = algo_performance_table(df, algos=algos)
    rows = {}
    for mode, label in [("or", f"{algo_a}_OR_{algo_b}"), ("and", f"{algo_a}_AND_{algo_b}")]:
        pred = ensemble_answer(df, algo_a, algo_b, mode=mode)
        c = confusion_counts_from_answers(df, pred)
        m = metrics_from_counts(c)
        rows[label] = {**c, **m}
    return pd.concat([base, pd.DataFrame(rows).T.round(3)])


#where two algorithms disagree: how often, and what share of positive-negative
def disagreement_analysis(df: pd.DataFrame, algo_a: str, algo_b: str) -> dict:
    dis = df[df[f"{algo_a}_answer"] != df[f"{algo_b}_answer"]]
    a_extra = dis[(dis[f"{algo_a}_answer"] == "P") & (dis[f"{algo_b}_answer"] == "N")]
    b_extra = dis[(dis[f"{algo_a}_answer"] == "N") & (dis[f"{algo_b}_answer"] == "P")]
    return {
        "n_disagree": len(dis),
        "pct_disagree": round(len(dis) / len(df), 4),
        f"{algo_a}_only_positive_n": len(a_extra),
        f"{algo_a}_only_positive_hit_rate": round((a_extra["radiologist_answer"] == "P").mean(), 3) if len(a_extra) else float("nan"),
        f"{algo_b}_only_positive_n": len(b_extra),
        f"{algo_b}_only_positive_hit_rate": round((b_extra["radiologist_answer"] == "P").mean(), 3) if len(b_extra) else float("nan"),
    }


#the time between an algorithm finishing its run and the radiologist's answer
def algo_lead_time_min(df: pd.DataFrame, algo: str) -> pd.Series:
    return (df["radiologist_sign_time"] - df[f"{algo}_finish_run"]).dt.total_seconds() / 60


#for each algorithm: what share of scans it finished before the radiologist's answers
def actionability_summary(df: pd.DataFrame, algos=ALGO_NAMES) -> pd.DataFrame:
    rows = []
    for algo in algos:
        lead = algo_lead_time_min(df, algo)
        in_time = lead > 0
        rows.append({
            "algo": algo,
            "n": len(df),
            "pct_in_time": in_time.mean(),
            "median_lead_min_when_in_time": lead[in_time].median(),
        })
    return pd.DataFrame(rows).round(3)


#prints several small tables side by side
def side_by_side(dfs: list, titles: list, gap: int = 8) -> None:
    blocks = []
    for d, t in zip(dfs, titles):
        text = d.to_string()
        lines = [t] + text.split("\n")
        width = max(len(l) for l in lines)
        lines = [l.ljust(width) for l in lines]
        blocks.append(lines)

    max_lines = max(len(b) for b in blocks)
    for b in blocks:
        b += [" " * len(b[0])] * (max_lines - len(b))

    for row in zip(*blocks):
        print((" " * gap).join(row))