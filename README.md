# Brain Bleed Detection and Evaluation

Data exploration and performance evaluation of three AI algorithms for detecting
intracranial hemorrhage (brain bleeds) on CT scans, deployed across two hospital
sites, each split into two patient departments (emergency vs. regular
hospitalization). This project compares the three algorithms and concludes with
recommendations for three audiences: **ML/Algo** (classification performance and
error patterns), **Product** (how findings should change the workflow), and
**Ops** (runtime, latency, site-level operational gaps).

> All data is synthetically generated for this project and contains no real
> patient information.

## Background

Intracranial hemorrhage (ICH) - bleeding inside the skull - is a time-critical
finding on CT scans, where faster detection can materially change patient
outcomes. AI triage tools are increasingly deployed alongside radiologists to
flag likely-positive scans so they can be pulled out of an otherwise
first-in-first-out reading queue and reviewed sooner.

This project simulates exactly that setup: three independently trained
detection algorithms, deployed across two hospital sites, each scanning every
case in parallel and producing a positive/negative call. Radiologists still
read every scan independently, regardless of the algorithms' predictions -
the radiologist's read is the ground truth used to evaluate the algorithms.
This analysis evaluates whether, and how well, each algorithm is actually fit
for that role: from a classification-accuracy, operational-speed, and
deployment-workflow perspective.

## Key findings

- Patient volume is unevenly split: one site handles roughly 70% of all scans
  versus 30% at the other, and inpatients outnumber ED cases at both sites
  (72% vs. 28% overall). ED patients also skew male (65% vs. 54% overall) -
  a patient-class effect rather than a site effect, consistent with men
  experiencing head trauma more often on average.
- Base positive rate is 9.5%, more than doubling between ED (4.7%) and
  inpatient (11.4%) scans. The two classes need to be evaluated separately,
  not pooled, or a trivial "always negative" baseline looks deceptively strong
  (~90% accuracy).
- The three algorithms sit at very different points on the sensitivity/PPV
  tradeoff (recall/precision, in general ML terms): algo1 is a conservative,
  high-specificity model (98% specificity, 51% sensitivity), algo2 is an
  aggressive, high-recall model (92% sensitivity, but 86% of its alerts are
  false alarms), and algo3 is a balanced model with the best F1 (0.73).
- The downside is that algo3 is also ~13x slower than the fastest algorithm
  (10 min mean runtime vs. 45s) and far less consistent, with a much wider
  spread of runtimes. It only beats the radiologist's independent read on 46%
  of scans overall, which is a real deployability constraint.
- Pairwise agreement tells a more nuanced story: algo1 and algo3 give the same
  answer on 93% of scans, but that's driven almost entirely by matching
  negative calls. Restricted to positive predictions specifically, the
  highest pairwise agreement is between algo2 and algo3, at 77%.

## Repo structure

```
├── brain_bleed_detection_and_evaluation.ipynb    # full walkthrough, Part 1 + Part 2
├── data_loader.py                                # load + clean + derive fields + data-quality report
├── exploration.py                                # Part 1: demographics, duration, prevalence, volume
├── performance.py                                # Part 2: confusion matrices, metrics, agreement, actionability
├── viz.py                                        # plotting for both parts
├── ICH_data.csv                                  # dataset 
├── requirements.txt
└── README.md
```

## Data

20,000 rows, two sites, two departments, three algorithms. Each row is one CT scan.

| Column | Description |
|---|---|
| `accession` | Unique scan identifier. |
| `site` | Hospital name. |
| `patient_class` | `ED` = emergency department patient, `IN` = inpatient (regular hospitalization). |
| `gender` | Patient's gender |
| `age` | Patient's age |
| `scan_timestamp` | When the CT scan was acquired (recorded automatically by the scanner). |
| `radiologist_answer` | Ground truth: the radiologist's independent read, `P` (positive) or `N` (negative) for ICH. |
| `radiologist_sign_time` | When the radiologist finished independently interpreting the scan. |
| `algos_start_run` | When all three algorithms began analyzing the scan (in parallel), after it reached the server. |
| `algo1_answer` / `algo2_answer` / `algo3_answer` | Each algorithm's prediction: `P` (positive) or `N` (negative). |
| `algo1_finish_run` / `algo2_finish_run` / `algo3_finish_run` | When each algorithm finished processing the scan. |

## Running it

```bash
pip install -r requirements.txt
jupyter notebook brain_bleed_detection_and_evaluation.ipynb
```

## Recommendations

**ML/Algo**
- Improve algo3's runtime first: a 3-4x reduction (to roughly 150-200s)
  without changing its classification logic would make it the strongest
  option across every axis evaluated here.
- Reduce algo2's false-positive rate: raising its decision threshold
  slightly could meaningfully improve precision without giving up much
  sensitivity.
- Raise algo1's true-positive count: this is its most significant weakness
  relative to the other two.

**Product**
- Differentiate alerts by algorithm reliability: since the three algorithms
  carry very different error profiles, their alerts could be visually
  distinguished for radiologists in the UI rather than presented uniformly.
- Build a retrospective-review workflow for algo3: while too slow for
  real-time triage, it could still run after the fact to flag cases the
  faster algorithms got wrong, route them for review, and feed confirmed
  misses back as training data.

**Ops**
- Give algo3 dedicated compute resources, which may resolve its runtime
  bottleneck.
- Investigate why one site's ED reads show no speed advantage over inpatient
  reads, unlike the other site - this could reflect a deliberate site
  practice, or an infrastructure issue silently blocking triage
  prioritization.
- Investigate the gap in how quickly algorithms begin processing after scan
  acquisition between the two sites (roughly double at one vs. the other) -
  the absolute impact is minor, but closing it could still help.
