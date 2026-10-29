# Healthcare Analytics course data

Public data files for the Healthcare Analytics graduate seminar (Fairfield University, Dolan School of
Business). Lab notebooks read these files by URL:

    https://raw.githubusercontent.com/stevenelliottjr/healthcare-analytics-course-data/main/data/<file>

| File | Used in | What it is |
|---|---|---|
| `data/lab03_hospitals.csv` | Lab 3, data quality | A copy of CMS Hospital General Information with deliberate errors planted for students to find. Do not use it for analysis. |
| `data/cms/cms_hospital_general_info.csv` | Most labs | Mirror of CMS Hospital General Information (`xubh-q36u`), 5,419 hospitals |
| `data/cms/cms_hrrp.csv` | Labs 2, 5, 6, 12 | Mirror of the Hospital Readmissions Reduction Program file (`9n3s-kdb3`), performance period 07/2021–06/2024 |
| `data/cms/cms_unplanned_visits.csv` | Labs 2, 4, 9–11 | Mirror of Unplanned Hospital Visits (`632h-zaca`); readmission measures cover 07/2023–06/2025 |
| `data/cms/cms_inpatient_690ddc6c_drg291.csv` | Lab 7 | Medicare Inpatient Hospitals by Provider and Service, data year 2024, DRG 291 only (2,587 hospitals) |
| `data/cdc/cdc_places_county.csv` | 2027 course, weeks 2–12 | CDC PLACES county data, 2025 release (`swc5-untb`), data year 2023: 10 measures (DIABETES, OBESITY, CSMOKING, BPHIGH, COPD, CHD, DEPRESSION, ACCESS2, CHECKUP, LPA), crude and age-adjusted. Kentucky and Pennsylvania have none of these measures in this release. Extracted 2026-10-29 |
| `data/cdc/cdc_acs_county_measures.csv` | 2027 course, weeks 2–12 | CDC Non-Medical Factor Measures for County (`i6u4-y3g4`), from the Census ACS 5-year 2017–2021: 9 measures, 3,143 counties (old Connecticut counties). Extracted 2026-10-29 |
| `data/course/hospital_county_crosswalk.csv` | 2027 course, weeks 3–12 | Course-built crosswalk from CMS Facility ID to 5-digit county FIPS, matched on state + county name: 5,338 of 5,419 matched; 65 territories not in the CDC county files; 16 to check by hand (CMS spelling errors) |

## The CMS mirror

Labs always try the live CMS source first. The mirror is a fallback for when data.cms.gov is down or
rate-limits a classroom of students downloading the same files at once. Snapshot taken 2026-10-26; CMS
refreshes Care Compare quarterly, so refresh the mirror before each term:

    python scripts/refresh_cms_mirror.py
    git add data/cms && git commit -m "Refresh CMS mirror" && git push

All files derive from public U.S. government data or are synthetic. None contain protected health information.

<!-- colab-course:start -->
## Course (Google Colab)

The whole course also runs in **Google Colab**, as a Plan B to Hex. The student notebooks are in
[`notebooks/`](notebooks/); each link below opens one in Colab. Solutions are not published.
Course home in Colab: [00_course_home.ipynb](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/00_course_home.ipynb).

**Start here, before week 1:**

1. Work through the [Primer: Python, pandas, and SQL](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/primer_python_pandas_sql.ipynb) at your own
   pace (3–4 hours, practice only, not graded). Stuck? The
   [answers](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/primer_python_pandas_sql_answers.ipynb) are open to you.
2. Do [Lab 0: Getting started in Colab](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/lab00_getting_started_colab.ipynb) (about 45 minutes). It
   ends with a check that prints `ready`.
3. Read the week 1 reading below.

### How the course works

**Each session (3 hours):** a student-led reading discussion (from week 3), a short concept segment with a live
demo, a 75-minute lab in pairs, and a share-out where each pair shows one result and explains one line of code.

**Each lab has a baseline and powerups.** Everyone finishes the **baseline** in the session; it is graded
*complete* or *revise*, with one free resubmission within a week. **Powerups** are optional depth. Complete at
least four over the term, chosen by you.

**Doing and submitting a lab (Colab):**

1. Open the lab from the table below (each link opens it in Colab) and click **File → Save a copy in Drive**.
   Rename your copy `Lab N — <your last name>`.
2. Work in your copy. Cells marked `# TODO` and *edit this cell* are yours.
3. **Runtime → Run all**, then **File → Save and pin revision**.
4. **Share** your copy with **steven.elliott@student.fairfield.edu** as **Editor**.

**AI policy.** AI may write the code; **you own it.** Anyone may be asked to explain any line they submit.
Weeks 2 and 5 are **unplugged**: no AI assistant.

**Weeks 10–11 and the API key.** Both labs run in **replay mode** in Colab by default (recorded examples; every
baseline step works). For live mode, ask the instructor for a key and add it in Colab's **Secrets** panel (key
icon, left sidebar) as `ANTHROPIC_API_KEY`, with notebook access on. Never paste a key into a cell.

**If a cell fails,** don't troubleshoot for more than 15 minutes. Post the error in the course channel. If CMS's
website is down, the labs switch to a course copy of the data automatically and say so. If Colab disconnects,
**Runtime → Run all**.

### Part 1 · Foundations: data, measurement, quality, place (weeks 1–4)

| Week | Topic | Read before the session | Lab | Due |
|---:|---|---|---|---|
| 1 | The U.S. healthcare data landscape | [Comment letter: Request for Information on Medicare Advantage Data (CMS-4207-NC)](https://brookings.edu/wp-content/uploads/2024/05/AdlerFiedler-MADataRFIResponse-FINAL.pdf) · *optional:* [What can be done to improve all-payer claims databases?](https://www.brookings.edu/articles/what-can-be-done-to-improve-all-payer-claims-databases) | [Lab 1: The U.S. healthcare data landscape](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/lab01_landscape.ipynb) |  |
| 2 | Measurement: rates, denominators, risk adjustment **(unplugged)** | [Hospital Readmission Risk: Isolating Hospital from Patient Effects](https://pmc.ncbi.nlm.nih.gov/articles/PMC5671772/) · *optional:* [The Hospital Readmissions Reduction Program: Learning from Failure of a Healthcare Policy](https://pmc.ncbi.nlm.nih.gov/articles/PMC6105419/) | [Lab 2: Measurement: rates, denominators, risk adjustment, suppression](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/lab02_measurement.ipynb) | **Milestone:** question brief |
| 3 | Data quality and honest numbers | [A Harmonized Data Quality Assessment Terminology and Framework for the Secondary Use of Electronic Health Record Data](https://pmc.ncbi.nlm.nih.gov/articles/PMC5051581/) · *optional:* [Potential Biases in Machine Learning Algorithms Using Electronic Health Record Data](https://pmc.ncbi.nlm.nih.gov/articles/PMC6347576/) | [Lab 3: Data quality and honest numbers](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/lab03_data_quality.ipynb) |  |
| 4 | Place, population, and equity | [PLACES: Local Data for Better Health](https://pmc.ncbi.nlm.nih.gov/articles/PMC9258452/) · *optional:* [A Social Vulnerability Index for Disaster Management](https://stacks.cdc.gov/view/cdc/134506/cdc_134506_DS1.pdf) | [Lab 4: Place, population, and equity](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/lab04_place_equity.ipynb) | **Milestone:** dataset documented |

In week 2, save a copy of the [Capstone template](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/capstone_template.ipynb) in Drive. Your milestones live in it all term.

### Part 2 · Prediction, cost, and communication (weeks 5–8)

| Week | Topic | Read before the session | Lab | Due |
|---:|---|---|---|---|
| 5 | Predicting outcomes I: regression, then trees **(unplugged)** | [Leakage and the reproducibility crisis in machine-learning-based science](https://pmc.ncbi.nlm.nih.gov/articles/PMC10499856/) · *optional:* [A systematic review shows no performance benefit of machine learning over logistic regression for clinical prediction models](https://ora.ox.ac.uk/objects/uuid:4167c905-5171-4fc7-b157-ff36d56a73db/files/m0c822b1760523fd587b9a6769e616049) | [Lab 5: Predicting outcomes I: regression, then trees](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/lab05_predicting_outcomes.ipynb) |  |
| 6 | Predicting outcomes II: evaluation and subgroups | [Dissecting racial bias in an algorithm used to manage the health of populations](https://www.ftc.gov/system/files/documents/public_events/1548288/privacycon-2020-ziad_obermeyer.pdf) · *optional:* [Calibration: the Achilles heel of predictive analytics](https://pmc.ncbi.nlm.nih.gov/articles/PMC6912996/) | [Lab 6: Predicting outcomes II: evaluation and subgroups](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/lab06_evaluation_subgroups.ipynb) | **Milestone:** analysis plan |
| 7 | What care costs: utilization and prices | [Early results from federal price transparency rule show difficulty in estimating the cost of care](https://www.healthsystemtracker.org/brief/early-results-from-federal-price-transparency-rule-show-difficultly-in-estimating-the-cost-of-care/) · *optional:* [Executive Summary: The Price Ain't Right? Hospital Prices and Health Spending on the Privately Insured](https://cowles.yale.edu/sites/default/files/publication-documents/2023-01/pricing_variation_exec_summary.pdf) | [Lab 7: What care costs: utilization and prices](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/lab07_what_care_costs.ipynb) |  |
| 8 | Communicating for decisions **(midterm)** | [Helping Patients Decide: Ten Steps to Better Risk Communication](https://pmc.ncbi.nlm.nih.gov/articles/PMC3218625/) · *optional:* [Dashboard Confusion](https://www.perceptualedge.com/articles/ie/dashboard_confusion.pdf) | [Lab 8: Midterm: communicating for decisions](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/lab08_midterm_app.ipynb) | **Midterm:** app (view-only link) |

### Part 3 · Working with AI (weeks 9–11)

| Week | Topic | Read before the session | Lab | Due |
|---:|---|---|---|---|
| 9 | How analysts work with AI now | [How Do Analysts Understand and Verify AI-Assisted Data Analyses?](https://arxiv.org/abs/2309.10947) · *optional:* [Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) + [We are Changing our Developer Productivity Experiment Design](https://metr.org/blog/2026-02-24-uplift-update/) | [Lab 9: How analysts work with AI now](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/lab09_working_with_ai.ipynb) |  |
| 10 | AI analysts: tool use over your data | [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) · *optional:* [MedAgentBench: A Realistic Virtual EHR Environment to Benchmark Medical LLM Agents](https://arxiv.org/abs/2501.14654) | [Lab 10: AI analysts: tool use over your data](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/lab10_ai_analyst_agent.ipynb) |  |
| 11 | Evaluating AI answers | [Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/) · *optional:* [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) | [Lab 11: Evaluating AI answers](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/lab11_evaluating_ai.ipynb) | **Milestone:** evaluation set (needs a live score: ask for a key) |

### Part 4 · Governance and the capstone (weeks 12–14)

| Week | Topic | Read before the session | Lab | Due |
|---:|---|---|---|---|
| 12 | Privacy, ethics, and governance | [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993) · *optional:* [De-Identification of Personal Information (NISTIR 8053)](https://nvlpubs.nist.gov/nistpubs/ir/2015/NIST.IR.8053.pdf) | [Lab 12: Privacy, ethics, and governance](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/lab12_privacy_governance.ipynb) |  |
| 13 | Work session and peer review | No reading: read your partner's draft | [Lab 13: Work session and peer review](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/lab13_peer_review.ipynb) | **Milestone:** draft brief |
| 14 | Showcase | No reading | [Lab 14: Showcase](https://colab.research.google.com/github/stevenelliottjr/healthcare-analytics-course-data/blob/main/notebooks/lab14_showcase.ipynb) | **Capstone final:** brief, 10-minute presentation, app, evaluated AI analysis |

### How you are graded

| Component | Weight |
|---|---:|
| Weekly labs, baseline (complete or revise) | 30% |
| Powerups (at least four, your choice) | 10% |
| Seminar participation, including leading one or two discussions | 15% |
| Midterm: an app for a reader (week 8) | 15% |
| Capstone milestones (weeks 2, 4, 6, 11, 13; 2% each) | 10% |
| Capstone final (week 14) | 20% |

Full rubrics are in the syllabus and in the midterm guide. Due dates for this term: [to be added].
<!-- colab-course:end -->
