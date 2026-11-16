# Data dictionary

## ndma_pakistan_floods_2022_snapshot.csv

One row per administrative region of Pakistan. Cumulative figures for the 2022 monsoon season, 14 June - 18 September 2022.

| Column | Attribute | Unit | Type | Description |
|---|---|---|---|---|
| `region_id` | - | - | - | Alternative label used in the manuscript (u1 ... u7) |
| `region` | - | - | - | AJ&K = Azad Jammu and Kashmir; GB = Gilgit-Baltistan; ICT = Islamabad Capital Territory; KP = Khyber Pakhtunkhwa |
| `deaths` | e1 | persons | loss | Total deaths |
| `injured` | e2 | persons | loss | Total injured |
| `roads_km` | e3 | km | loss | Length of roads damaged |
| `bridges` | e4 | count | loss | Bridges damaged |
| `houses` | e5 | count | loss | Houses damaged (partially and fully) |
| `livestock` | e6 | head | loss | Livestock lost |
| `affected_population` | e7 | persons | loss | Affected population |

Column totals: 1,545 deaths; 12,860 injured; 12,735 km; 375 bridges; 1,943,978 houses; 943,909 livestock; 33,046,329 people. These totals coincide with the cumulative national figures of the NDMA daily situation report of 18 September 2022.

Known caveats (see Section 9.4 of the manuscript):

* The figures are a provisional cumulative snapshot. By 18 November 2022 the national totals had risen by 0-23 % (see below).
* All indicators are loss-type. No indicator of relief delivered or reconstruction completed is included.
* Zeros may mean "no loss" or "not reported" (e.g. roads in AJ&K, livestock in GB).
* Some values are rounded estimates (e.g. 500,000 livestock in Balochistan).
* Counts are absolute, not per capita.

## ndma_national_totals_revision.csv

National totals on the snapshot date and final totals (NDMA situation report of 18 November 2022, as reported by OCHA Situation Report No. 11). The affected-population figure was not revised.

| Indicator | 18 Sep 2022 | 18 Nov 2022 | Revision |
|---|---:|---:|---:|
| Deaths | 1,545 | 1,739 | +12.6 % |
| Injured | 12,860 | 12,867 | +0.1 % |
| Roads (km) | 12,735 | 13,115 | +3.0 % |
| Bridges | 375 | 439 | +17.1 % |
| Houses | 1,943,978 | 2,288,481 | +17.7 % |
| Livestock | 943,909 | 1,164,270 | +23.3 % |
| Affected population | 33,046,329 | about 33 million | n/a |

## config_pakistan2022.json

* `attributes`: for each attribute id the data column, label, type (`loss` or `capacity`) and global weight.
* `stages`: active attribute ids per stage.
* `tolerance`: relative interval tolerance (a number, or an object with one value per attribute id).
* `normalisation`: `minmax` (baseline), `max`, `sum` or `vector`.
* `stage_emphasis_profiles`: named weight vectors over the stages for the combined index.
