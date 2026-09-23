# Brain Bleed Algorithm Evaluation

Data exploration and performance evaluation of three AI algorithms for detecting
intracranial hemorrhage (brain bleeds) on CT scans, deployed across two hospital
sites. Structured for three audiences: **ML/Algo** (classification performance and
error patterns), **Product** (how findings should change the workflow), and
**Ops** (runtime, latency, site-level operational gaps).

> All data is synthetically generated for this project and contains no real
> patient information.

## Background

Intracranial hemorrhage (ICH) — bleeding inside the skull — is a time-critical
finding on CT scans, where faster detection can materially change patient
outcomes. AI triage tools are increasingly deployed alongside radiologists to
flag likely-positive scans so they can be pulled out of an otherwise
first-in-first-out reading queue and reviewed sooner.

This project simulates exactly that setup: three independently trained
detection algorithms, deployed across two hospital sites, each scanning every
case in parallel and producing a positive/negative call. Radiologists still
read every scan independently — their read is the ground truth used to
evaluate the algorithms — but each algorithm's output could, in principle,
both reorder the queue toward urgent cases and assist the radiologist on
ambiguous findings. This analysis evaluates whether, and how well, each
algorithm is actually fit for that role — from a classification-accuracy,
operational-speed, and deployment-workflow perspective.

## Key findings

- Base positive rate is 9.5%, more than doubling between ED (4.7%) and
  inpatient (11.4%) scans — the two classes need to be evaluated separately,
  not pooled, or a trivial "always negative" baseline looks deceptively strong
  (~90% accuracy).
- The three algorithms sit at very different points on the sensitivity/PPV
  tradeoff: a conservative high-specificity model (98% specificity, 51%
  sensitivity), an aggressive high-recall model (92% sensitivity, but 86% of
  its alerts are false alarms), and a balanced model with the best F1 (0.73).
- The balanced model is also ~13x slower than the fastest one (10 min mean
  runtime vs. 45s), and only beats the radiologist's independent read on 46%
  of scans overall — a real deployability constraint the confusion matrix
  alone doesn't show.
- Age shows the *opposite* of the expected clinical risk pattern in this
  dataset (flat ~11–12% from 0–50, declining after) — called out explicitly
  as a synthetic-data artifact rather than over-interpreted as a real finding.

## Repo structure

```
├── brain_bleed_algorithm_evaluation.ipynb   # full walkthrough, Part 1 + Part 2
├── data_loader.py                            # load + clean + derive fields + data-quality report
├── exploration.py                            # Part 1: demographics, duration, prevalence, volume
├── performance.py                            # Part 2: confusion matrices, metrics, agreement, actionability
├── viz.py                                    # matplotlib/seaborn plotting for both parts
├── data/ICH_data.csv                         # dataset (synthetic)
├── requirements.txt
└── README.md
```

## Data

~20,000 rows, two sites, three algorithms. Each row is one CT scan.

| Column | Description |
|---|---|
| `accession` | Unique scan identifier. |
| `site` | Hospital/site name. |
| `patient_class` | `ED` = emergency department patient, `IN` = inpatient (regular hospitalization). |
| `gender` | Patient's gender. |
| `age` | Patient's age. |
| `scan_timestamp` | When the CT scan was acquired (recorded automatically by the scanner). |
| `radiologist_answer` | Ground truth: the radiologist's independent read, `P` (positive) or `N` (negative) for ICH. |
| `radiologist_sign_time` | When the radiologist finished independently interpreting the scan. |
| `algos_start_run` | When all three algorithms began analyzing the scan (in parallel), after it reached the server. |
| `algo1_answer` / `algo2_answer` / `algo3_answer` | Each algorithm's prediction: `P` (positive) or `N` (negative). |
| `algo1_finish_run` / `algo2_finish_run` / `algo3_finish_run` | When each algorithm finished processing the scan. |

## Running it

```bash
pip install -r requirements.txt
jupyter notebook brain_bleed_algorithm_evaluation.ipynb
```

## Future work

- Reweight confusion matrices/metrics for the class imbalance and check
  whether the algorithm ranking changes.
- Extend the sensitivity/specificity subgroup analysis to age bins.
- Move from binary P/N outputs to continuous scores per algorithm to enable
  ROC-curve analysis and threshold tuning.
- Drill into the aggressive model's specific disagreement cases with the
  other two.
