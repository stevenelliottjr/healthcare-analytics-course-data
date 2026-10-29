# Healthcare Analytics course data and materials

Materials and public data files for **DATA 6900: Healthcare Analytics**, a graduate topics seminar at
Fairfield University's Dolan School of Business (Spring 2027, Tuesdays 6:30–9:30 pm, online, for MSAIBA
and Egan MPH students).

## Start here: the Spring 2027 course

**[`course2027/`](course2027/README.md)** is the course. It holds the course home, the 14 weekly briefs,
one marimo notebook per build week, the templates (provenance record, defend-a-number, data card,
compliance checklist, human sign-off, transcript guide, peer review, app rubric), and the readings list.

No programming is required. Students run the notebooks on [molab](https://molab.marimo.io) (marimo's
free hosted service) and use any AI assistant to write and explain code. Only public, aggregate data
goes into any AI tool; no PHI, ever.

| | |
|---|---|
| Course home | [course2027/README.md](course2027/README.md) |
| Weekly briefs | [course2027/weeks/](course2027/weeks/) |
| Notebooks | [course2027/notebooks/](course2027/notebooks/) |
| Templates | [course2027/templates/](course2027/templates/) |
| Readings | [course2027/READINGS.md](course2027/READINGS.md) |

## The data

Every course notebook reads these files by URL through a shared setup cell. It loads a dated snapshot
from this mirror (never the live CMS or CDC site, which can refuse scripted downloads or change mid-term)
and records each load, including the snapshot date, in a provenance table the student can read.

    https://raw.githubusercontent.com/stevenelliottjr/healthcare-analytics-course-data/main/data/<file>

| File | Used in | What it is |
|---|---|---|
| `data/cms/cms_hospital_general_info.csv` | Weeks 1–12 | Mirror of CMS Hospital General Information (`xubh-q36u`), 5,419 hospitals. Snapshot 2026-10-26 |
| `data/cms/cms_hrrp.csv` | Weeks 2–12 | Mirror of the Hospital Readmissions Reduction Program file (`9n3s-kdb3`), performance period 07/2021–06/2024 |
| `data/cms/cms_unplanned_visits.csv` | Weeks 2–12 | Mirror of Unplanned Hospital Visits (`632h-zaca`); readmission measures cover 07/2023–06/2025 |
| `data/cdc/cdc_places_county.csv` | Weeks 2–12 | CDC PLACES county data, 2025 release (`swc5-untb`), data year 2023: 10 measures (DIABETES, OBESITY, CSMOKING, BPHIGH, COPD, CHD, DEPRESSION, ACCESS2, CHECKUP, LPA), crude and age-adjusted. Kentucky and Pennsylvania have none of these measures in this release. Extracted 2026-10-29 |
| `data/cdc/cdc_acs_county_measures.csv` | Weeks 2–12 | CDC Non-Medical Factor Measures for County (`i6u4-y3g4`), from the Census ACS 5-year 2017–2021: 9 measures, 3,143 counties (old Connecticut counties). Extracted 2026-10-29 |
| `data/course/hospital_county_crosswalk.csv` | Weeks 3–12 | Course-built crosswalk from CMS Facility ID to 5-digit county FIPS, matched on state + county name: 5,338 of 5,419 matched; 65 territories not in the CDC county files; 16 to check by hand (CMS spelling errors) |
| `data/lab03_hospitals.csv` | Week 4 | A copy of CMS Hospital General Information with deliberate errors planted for students to find. Do not use it for analysis. |
| `data/cms/cms_inpatient_690ddc6c_drg291.csv` | Power-ups | Medicare Inpatient Hospitals by Provider and Service, data year 2024, DRG 291 only (2,587 hospitals) |

### Refreshing the CMS mirror

CMS refreshes Care Compare quarterly. Refresh the mirror before each term, then update the snapshot date
in the table above and in `MIRROR_SNAPSHOT` in the setup cell of every notebook in `course2027/notebooks/`
(the cell is identical in each):

    python scripts/refresh_cms_mirror.py
    git add data/cms && git commit -m "Refresh CMS mirror" && git push

All files derive from public U.S. government data or are synthetic. None contain protected health
information.

## Earlier builds (superseded)

`notebooks/` holds the October 2026 Python-based version of the course, built for Hex and Google Colab,
with a Python/pandas/SQL primer and labs 0–14. It was replaced on 2026-10-28 by `course2027/` after
faculty review: the new course assumes no programming, runs on marimo, and is built around one data
aggregator per student. The old notebooks are kept for reference and are not maintained.
