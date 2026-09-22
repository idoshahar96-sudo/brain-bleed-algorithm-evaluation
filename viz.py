"""
viz.py
----------------
Plotting helpers, for both part 1 and part 2 of the analysis
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

sns.set_theme(style="whitegrid", palette="deep")
ALGO_NAMES = ["algo1", "algo2", "algo3"]


#scan volume by site/class, gender split and age split 
def fig_population_overview(df: pd.DataFrame, combo_palette=None):
    from matplotlib.ticker import PercentFormatter
    df = df.copy()
    df["site_class"] = df["site"] + "\n" + df["patient_class"]
    total_n = len(df)

    site_class_order = ["healthy_vibes\nED", "healthy_vibes\nIN",
                         "best_doctors\nED", "best_doctors\nIN"]

    if combo_palette is None:
        combo_palette = {
            "healthy_vibes\nED": "#7FB3D5",
            "healthy_vibes\nIN": "#1F4E79",
            "best_doctors\nED": "#F5B183",
            "best_doctors\nIN": "#C0500D",
        }

    gender_palette = {"male": "#6A4C93", "female": "#1F9E89"}

    def pct_label(x):
        return f"{x:,.0f}\n({x / total_n * 100:.1f}%)"

    def add_subtitle(ax, text, fontsize=8):
        ax.text(0.5, 1.0, text, transform=ax.transAxes, ha="center", va="bottom",
                fontsize=fontsize, style="italic", color="dimgray")

    fig, axes = plt.subplots(3, 2, figsize=(13, 16.5))

    sns.countplot(data=df, x="site", hue="patient_class", ax=axes[0, 0])
    axes[0, 0].set_title("Scan volume by site & patient class", pad=18, fontsize=14)
    add_subtitle(axes[0, 0], "% of full dataset (n=20,000)")
    axes[0, 0].set_xlabel("")
    axes[0, 0].margins(y=0.18)
    for container in axes[0, 0].containers:
        axes[0, 0].bar_label(container, fontsize=12, fmt=pct_label)

    sns.countplot(data=df, x="patient_class", hue="gender", palette=gender_palette, ax=axes[0, 1])
    axes[0, 1].set_title("Patient class split by gender")
    axes[0, 1].set_xlabel("")
    axes[0, 1].margins(y=0.18)
    for container in axes[0, 1].containers:
        axes[0, 1].bar_label(container, fontsize=10, fmt=pct_label)

    sns.histplot(data=df, x="age", hue="patient_class", bins=30, kde=True,
                 element="step", ax=axes[1, 0])
    axes[1, 0].set_title("Age distribution by patient class")

    sns.histplot(data=df, x="age", hue="site", bins=30, kde=True,
                 element="step", ax=axes[1, 1])
    axes[1, 1].set_title("Age distribution by site")

    pct_df = (
        df.groupby(["site_class", "gender"]).size()
        / df.groupby("site_class").size()
        * 100
    ).rename("pct").reset_index()
    sns.barplot(data=pct_df, x="site_class", y="pct", hue="gender", order=site_class_order,
                palette=gender_palette, ax=axes[2, 0])
    axes[2, 0].set_title("Gender split by site & patient class", pad=18)
    add_subtitle(axes[2, 0], "% within each site + class group")
    axes[2, 0].set_xlabel("")
    axes[2, 0].set_ylabel("Percent")
    axes[2, 0].margins(y=0.15)
    axes[2, 0].yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
    for container in axes[2, 0].containers:
        axes[2, 0].bar_label(container, fmt=lambda x: f"{x:.1f}%", fontsize=11)

    sns.histplot(data=df, x="age", hue="site_class", palette=combo_palette,
                 bins=30, kde=True, element="step", ax=axes[2, 1])
    axes[2, 1].set_title("Age distribution by site & patient class")
    leg1 = axes[2, 1].get_legend()
    if leg1:
        leg1.set_title("Site / Class", prop={"size": 12})
        for text in leg1.get_texts():
            text.set_fontsize(11)
        leg1.set_bbox_to_anchor((0.0, 1.0))
        leg1._loc = 2  # upper left

    fig.tight_layout()
    return fig

#ICH prevalence according to radiologist answer: overall, by patient class, by site, and combined
def fig_prevalence(df: pd.DataFrame):
    from matplotlib.ticker import PercentFormatter
    df = df.copy()
    df["site_class"] = df["site"] + "\n" + df["patient_class"]
    total_n = len(df)

    fig, axes = plt.subplots(2, 2, figsize=(13, 10))

    n_pos = int(df["rad_positive"].sum())
    n_neg = total_n - n_pos
    axes[0, 0].bar(["ICH Negative", "ICH Positive"], [n_neg, n_pos],
                    color=["#4C72B0", "#C44E52"])
    axes[0, 0].set_title("Overall ICH prevalence")
    axes[0, 0].set_ylabel("Number of scans")
    axes[0, 0].margins(y=0.15)
    for x, n in zip(["ICH Negative", "ICH Positive"], [n_neg, n_pos]):
        axes[0, 0].text(x, n, f"{n:,}\n({n / total_n:.1%})", ha="center", va="bottom", fontsize=10)

    prev_class = df.groupby("patient_class")["rad_positive"].mean()
    prev_class.plot(kind="bar", ax=axes[0, 1], color=["#4C72B0", "#DD8452"])
    axes[0, 1].set_title("ICH prevalence by patient class")
    axes[0, 1].set_ylabel("Positive rate (radiologist)")
    axes[0, 1].set_xlabel("Patient Class")
    axes[0, 1].tick_params(axis="x", rotation=0)
    axes[0, 1].margins(y=0.12)
    axes[0, 1].yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))
    for container in axes[0, 1].containers:
        axes[0, 1].bar_label(container, fmt=lambda x: f"{x:.1%}", fontsize=9)

    prev_site = df.groupby("site")["rad_positive"].mean()
    prev_site.plot(kind="bar", ax=axes[1, 0], color=["#55A868", "#C44E52"])
    axes[1, 0].set_title("ICH prevalence by site")
    axes[1, 0].set_ylabel("Positive rate (radiologist)")
    axes[1, 0].set_xlabel("Site")
    axes[1, 0].tick_params(axis="x", rotation=0)
    axes[1, 0].margins(y=0.12)
    axes[1, 0].yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))
    for container in axes[1, 0].containers:
        axes[1, 0].bar_label(container, fmt=lambda x: f"{x:.1%}", fontsize=9)

    prev_combo = df.groupby("site_class")["rad_positive"].mean()
    site_class_order = ["healthy_vibes\nED", "healthy_vibes\nIN",
                         "best_doctors\nED", "best_doctors\nIN"]
    prev_combo = prev_combo.reindex(site_class_order)
    prev_combo.plot(kind="bar", ax=axes[1, 1], color=["#7FB3D5", "#1F4E79", "#F5B183", "#C0500D"])
    axes[1, 1].set_title("ICH prevalence by site & patient class")
    axes[1, 1].set_ylabel("Positive rate (radiologist)")
    axes[1, 1].set_xlabel("")
    axes[1, 1].tick_params(axis="x", rotation=0)
    axes[1, 1].margins(y=0.15)
    axes[1, 1].yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))
    for container in axes[1, 1].containers:
        axes[1, 1].bar_label(container, fmt=lambda x: f"{x:.1%}", fontsize=9)

    fig.tight_layout()
    return fig


#distribution of treatment duration overall, and broken down by site & patient class
def fig_duration_distribution(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    sns.histplot(data=df, x="duration_min", bins=50, kde=True, ax=axes[0])
    axes[0].set_title("Treatment duration (all scans)")
    axes[0].set_xlabel("Minutes")

    sns.boxplot(data=df, x="site", y="duration_min", hue="patient_class", ax=axes[1])
    axes[1].set_title("Duration by site & patient class")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Minutes")

    fig.tight_layout()
    return fig


#heatmap of scan volume by hour of day x day of week, to spot caseload patterns
def fig_volume_heatmap(pivot: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(pivot, cmap="mako", ax=ax, cbar_kws={"label": "# scans"})
    ax.set_title("Scan volume by hour of day and day of week")
    ax.set_xlabel("")
    ax.set_ylabel("Hour of day")
    fig.tight_layout()
    return fig


#confusion matrix heatmap for each algorithm vs the radiologist ground truth
def fig_confusion_matrices(df, confusion_counts_fn, format_counts_fn, algos=ALGO_NAMES):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6))
    for ax, algo in zip(axes, algos):
        c = confusion_counts_fn(df, algo)
        c_fmt = format_counts_fn(c)

        mat = np.array([[c["TP"], c["FN"]], [c["FP"], c["TN"]]])
        labels = np.array([[c_fmt["TP"], c_fmt["FN"]], [c_fmt["FP"], c_fmt["TN"]]])

        sns.heatmap(mat, annot=labels, fmt="", cmap="Blues", cbar=False, ax=ax,
                    xticklabels=["Pred P", "Pred N"], yticklabels=["Actual P", "Actual N"])
        ax.set_title(algo)

    fig.suptitle("Confusion matrices vs radiologist ground truth", fontsize=16, y=1.02)
    fig.text(0.5, 0.95,
              "Percentages are row-wise, share of ground truth",
              ha="center", fontsize=12, style="italic", color="dimgray")
    fig.tight_layout()
    return fig


#bar chart comparing the six metrics within each algorithm
def fig_metrics_bar(metrics_table: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(9, 5))
    metrics_table[["sensitivity", "specificity", "PPV", "NPV", "accuracy", "F1"]].plot(
        kind="bar", ax=ax
    )
    ax.set_title("All metrics per algorithm")
    ax.set_ylabel("Score")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")

    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", fontsize=8, padding=2)

    fig.tight_layout()
    return fig


#bar chart comparing the three algorithms within each metric
def fig_metrics_bar_by_metric(metrics_table: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 5))
    subset = metrics_table[["sensitivity", "specificity", "PPV", "NPV", "accuracy", "F1"]].T
    subset.plot(kind="bar", ax=ax)
    ax.set_title("Metric-by-metric comparison across algorithms")
    ax.set_ylabel("Score")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Algorithm", bbox_to_anchor=(1.02, 1), loc="upper left")

    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", fontsize=8, padding=2)

    fig.tight_layout()
    return fig


#grid comparing algorithm performance (F1 and accuracy) across three breakdown
def fig_performance_by_breakdown(by_site, by_class, by_combo, metrics=("F1", "sensitivity")):
    combo = by_combo.copy()
    combo["group"] = combo["site"] + "\n\n" + combo["patient_class"]

    breakdowns = [
        ("By site", by_site, "site"),
        ("By patient class", by_class, "patient_class"),
        ("By site + patient class", combo, "group"),
    ]

    fig, axes = plt.subplots(len(metrics), 3, figsize=(15, 4.6 * len(metrics)), squeeze=False)

    legend_handles, legend_labels = None, None

    for row, metric in enumerate(metrics):
        for col, (title, table, x_col) in enumerate(breakdowns):
            ax = axes[row, col]
            sns.barplot(data=table, x=x_col, y=metric, hue="algo", ax=ax)
            ax.set_title(f"{metric.capitalize()} {title}", fontsize=11)
            ax.set_ylabel(metric if col == 0 else "")
            ax.set_xlabel("")
            ax.set_ylim(0, 1)
            ax.tick_params(axis="x", rotation=0)

            if metric.lower() == "accuracy":
                ax.margins(y=0.15)

            for container in ax.containers:
                ax.bar_label(container, fmt=lambda x: f"{x:.2f}", fontsize=7)

            if legend_handles is None:
                legend_handles, legend_labels = ax.get_legend_handles_labels()
            if ax.legend_ is not None:
                ax.legend_.remove()

    fig.legend(legend_handles, legend_labels, title="Algorithm", fontsize=12,
               title_fontsize=13, loc="upper center", bbox_to_anchor=(0.5, 1.06),
               ncol=len(legend_labels))

    fig.suptitle("Algorithm performance across Sites and Classes", fontsize=15, y=1.12)
    fig.tight_layout()
    return fig


#boxplot of each algorithm's runtime distribution
def fig_runtime_boxplot(df: pd.DataFrame, algos=ALGO_NAMES):
    fig, ax = plt.subplots(figsize=(8, 5))
    melt = df[[f"{a}_runtime_s" for a in algos]].melt(var_name="algo", value_name="runtime_s")
    melt["algo"] = melt["algo"].str.replace("_runtime_s", "", regex=False)
    sns.boxplot(data=melt, x="algo", y="runtime_s", ax=ax)
    ax.set_title("Algorithm runtime distribution")
    ax.set_ylabel("Runtime (seconds)")
    ax.set_xlabel("")
    fig.tight_layout()
    return fig


#ICH prevalence by age group, overall + split by patient class
def fig_age_prevalence(df: pd.DataFrame, age_order=None):
    from matplotlib.ticker import PercentFormatter
    fig, axes = plt.subplots(1, 2, figsize=(16, 4.5))

    prev_age = df.groupby("age_group", observed=True)["rad_positive"].mean()
    if age_order is not None:
        prev_age = prev_age.reindex(age_order)
    prev_age.plot(kind="bar", ax=axes[0], color="#C44E52")
    axes[0].set_title("ICH prevalence by age group")
    axes[0].set_ylabel("Positive rate (radiologist)")
    axes[0].set_xlabel("Age group")
    axes[0].tick_params(axis="x", rotation=45)
    axes[0].margins(y=0.12)
    axes[0].yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))
    for container in axes[0].containers:
        axes[0].bar_label(container, fmt=lambda x: f"{x:.1%}", fontsize=8)

    by_class = df.groupby(["age_group", "patient_class"], observed=True)["rad_positive"].mean().unstack()
    if age_order is not None:
        by_class = by_class.reindex(age_order)
    by_class.plot(kind="bar", ax=axes[1])
    axes[1].set_title("ICH prevalence by age group, split by patient class")
    axes[1].set_ylabel("Positive rate (radiologist)")
    axes[1].set_xlabel("Age group")
    axes[1].tick_params(axis="x", rotation=45)
    axes[1].margins(y=0.12)
    axes[1].yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))
    for container in axes[1].containers:
        axes[1].bar_label(container, fmt=lambda x: f"{x:.1%}", fontsize=7)

    fig.tight_layout()
    return fig


#draws one agreement heatmap onto a given axis 
def _draw_agreement_heatmap(ax, agreement: pd.DataFrame, title: str = None, subtitle: str = None):
    sns.heatmap(agreement, annot=True, fmt=".2f", cmap="viridis", vmin=0, vmax=1, ax=ax, cbar=True)
    title = title or "Pairwise agreement between algorithms"
    if subtitle:
        title += f"\n({subtitle})"
    ax.set_title(title)


#heatmap of pairwise call-agreement rate between each pair of algorithms
def fig_agreement_heatmap(agreement: pd.DataFrame, title: str = None, subtitle: str = None):
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    _draw_agreement_heatmap(ax, agreement, title=title, subtitle=subtitle)
    fig.tight_layout()
    return fig


#two agreement heatmaps side by side in one figure
def fig_agreement_heatmap_pair(agreement_a: pd.DataFrame, agreement_b: pd.DataFrame,
                                title_a: str = None, title_b: str = None):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    _draw_agreement_heatmap(axes[0], agreement_a, title=title_a)
    _draw_agreement_heatmap(axes[1], agreement_b, title=title_b)
    fig.tight_layout()
    return fig


#bar chart of the share of scans each algorithm finished before the radiologist's answer
def fig_actionability(summary_table: pd.DataFrame):
    from matplotlib.ticker import PercentFormatter
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(summary_table["algo"], summary_table["pct_in_time"], color=["#4C72B0", "#DD8452", "#C44E52"])
    ax.set_title("Share of scans where the algorithm finished before the radiologist's read")
    ax.set_ylabel("% finished in time")
    ax.set_ylim(0, 1.08)
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))
    for x, y in zip(summary_table["algo"], summary_table["pct_in_time"]):
        ax.text(x, y + 0.02, f"{y:.1%}", ha="center", fontsize=10)
    fig.tight_layout()
    return fig


#compares pct_in_time and median lead time across multiple subsets
def fig_actionability_by_subset(subset_tables: dict):
    from matplotlib.ticker import PercentFormatter

    algo_palette = {"algo1": "#E63946", "algo2": "#457B9D", "algo3": "#F4A300"}

    rows = []
    for label, table in subset_tables.items():
        t = table.copy()
        n = int(t["n"].iloc[0])
        t["subset"] = f"{label}\n(n={n:,})"
        rows.append(t)
    combined = pd.concat(rows, ignore_index=True)
    subset_order = [f"{label}\n(n={int(t['n'].iloc[0]):,})" for label, t in subset_tables.items()]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.3))

    sns.barplot(data=combined, x="subset", y="pct_in_time", hue="algo", order=subset_order,
                palette=algo_palette, ax=axes[0])
    axes[0].set_title("Share of scans finished in time")
    axes[0].set_ylabel("% finished in time")
    axes[0].set_xlabel("")
    axes[0].set_ylim(0, 1.1)
    axes[0].yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))
    axes[0].margins(y=0.12)
    for container in axes[0].containers:
        axes[0].bar_label(container, fmt=lambda x: f"{x:.1%}", fontsize=8)
    axes[0].tick_params(axis="x", rotation=0)
    axes[0].legend(title="Algorithm", loc="lower center", bbox_to_anchor=(0.5, 1.12),
                    ncol=3, frameon=True)

    sns.barplot(data=combined, x="subset", y="median_lead_min_when_in_time", hue="algo",
                order=subset_order, palette=algo_palette, ax=axes[1])
    axes[1].set_title("Median lead time when finished in time")
    axes[1].set_ylabel("Minutes")
    axes[1].set_xlabel("")
    axes[1].margins(y=0.15)
    for container in axes[1].containers:
        axes[1].bar_label(container, fmt=lambda x: f"{x:.1f}", fontsize=8)
    axes[1].tick_params(axis="x", rotation=0)
    axes[1].legend_.remove()

    fig.tight_layout()
    return fig