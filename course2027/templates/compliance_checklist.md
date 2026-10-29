# Compliance checklist

Run on your aggregator in week 7, and again before weeks 8, 12 and 14. Each item needs **evidence**: a row count, a cell output, or one sentence. A tick with no evidence doesn't pass.

**Background:** PHI (protected health information) is individually identifiable health information. Course data is public, facility-level (hospital) or county-level aggregate data from CMS and CDC, and it is not PHI. These checks make sure your work stays that way.

## A. What's in the layer

| # | Check | Pass? | Evidence |
|---|---|---|---|
| A1 | Every source is public and published as aggregate data (hospital or county level). | | |
| A2 | No column describes an individual person (no names, birth dates, addresses, record numbers or similar). | | |
| A3 | Identifiers are facility or geography codes only (for example, CMS facility ID, county FIPS). | | |
| A4 | No data from my workplace or any non-public source. | | |

## B. Small cells and suppression

| # | Check | Pass? | Evidence |
|---|---|---|---|
| B1 | Values the publisher withheld ("Too Few to Report", "Not Available", "N/A", etc.) are still text in my layer. None were converted to zero or to a number. | | count of text values per column |
| B2 | I did not back-calculate any withheld value from other columns. | | |
| B3 | My app doesn't show a count where the source shows a suppressed value. | | |
| B4 | If I cite a small-cell threshold, I name the policy and link the page I read. (Otherwise, write "not cited".) | | |

## C. What I gave AI tools

| # | Check | Pass? | Evidence |
|---|---|---|---|
| C1 | I only pasted public, aggregate data, code and my own writing into AI tools. | | |
| C2 | No passwords, API keys or other credentials appear in my notebook, app or transcripts. | | |
| C3 | I reviewed my transcripts for this check. Anything I shouldn't have shared is noted here honestly. | | |

## D. What I publish

| # | Check | Pass? | Evidence |
|---|---|---|---|
| D1 | My app shows where its numbers came from (provenance visible). | | |
| D2 | My app says what's excluded and why. | | |

**Signed (name, date):**

I checked every item above myself.
