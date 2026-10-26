"""Refresh data/cms/ from the live CMS sources. Run before each term, then commit and push."""
import json
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "data" / "cms"
CMS_CATALOG = "https://data.cms.gov/provider-data/api/1/metastore/schemas/dataset/items"
CMS_IDS = {
    "hospital_general_info": "xubh-q36u",
    "hrrp": "9n3s-kdb3",
    "unplanned_visits": "632h-zaca",
}
# Lab 7: one DRG from Medicare Inpatient Hospitals by Provider and Service. Each data year has its own
# dataset id; when it changes, update it here AND in lab 7, and delete the old mirror file.
INPATIENT_PROVIDER_SERVICE = "690ddc6c-2767-4618-b277-420ffb2bf27c"
DRGS = ["291"]


def get(url, params=None, timeout=300) -> bytes:
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "healthcare-analytics-course/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, identifier in CMS_IDS.items():
        item = json.loads(get(f"{CMS_CATALOG}/{identifier}", timeout=60))
        url = next(d["downloadURL"] for d in item["distribution"] if d.get("mediaType") == "text/csv")
        (OUT / f"cms_{name}.csv").write_bytes(get(url))
        print("wrote", f"cms_{name}.csv")
    for drg in DRGS:
        url, rows, offset = f"https://data.cms.gov/data-api/v1/dataset/{INPATIENT_PROVIDER_SERVICE}/data", [], 0
        while True:
            chunk = json.loads(get(url, {"filter[DRG_Cd]": drg, "size": 5000, "offset": offset}))
            rows += chunk
            if len(chunk) < 5000:
                break
            offset += 5000
        name = f"cms_inpatient_{INPATIENT_PROVIDER_SERVICE[:8]}_drg{drg}.csv"
        pd.DataFrame(rows).to_csv(OUT / name, index=False)
        print("wrote", name, len(rows), "rows")


if __name__ == "__main__":
    main()
