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

## The CMS mirror

Labs always try the live CMS source first. The mirror is a fallback for when data.cms.gov is down or
rate-limits a classroom of students downloading the same files at once. Snapshot taken 2026-10-26; CMS
refreshes Care Compare quarterly, so refresh the mirror before each term:

    python scripts/refresh_cms_mirror.py
    git add data/cms && git commit -m "Refresh CMS mirror" && git push

All files derive from public U.S. government data or are synthetic. None contain protected health information.
