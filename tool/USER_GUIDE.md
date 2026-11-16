# DCFSS decision-support tools: user guide

Two tools produce the same results. Neither requires knowledge of fuzzy mathematics.

## A. Spreadsheet calculator (`DCFSS_Calculator.xlsx`)

Works in Microsoft Excel or LibreOffice Calc. Pre-sized for seven regions and seven indicators.

1. Open the sheet **Inputs**. Only the yellow cells are edited.
2. Type the figures of the situation report: one row per region, one column per indicator. Rename regions or indicators if needed.
3. In the row **Type**, write `loss` if a larger value is worse (deaths, damage) or `capacity` if a larger value is better (for example relief coverage).
4. In the row **Weight**, enter the importance of each indicator on any positive scale. The weights are rescaled automatically.
5. Enter the **reporting tolerance** (0.10 = the figures may be wrong by about 10 %).
6. In the **stage activation** table, write 1 where an indicator matters for a stage and 0 where it does not.
7. Read the sheet **Results**: for each stage the regions appear in priority order with their severity index, the band of the index and their tier. The sheet **Calc** shows every intermediate step.

How to read the output:

* **Severity index**: 0 = no reported loss; 1 = worst region on every active indicator. Priority 1 = most severe.
* **Band**: range of the score if all figures were wrong by up to the tolerance.
* **Tier**: regions with the same tier number have overlapping bands. Treat them as equal priority; do not rely on their order.
* **Combined index**: weighted mix of the three stage indices. Put more weight on the Impact stage in the first days and move it towards Recovery later.

## B. Command-line tool (`code/dcfss_tool.py`)

For any number of regions, indicators and stages.

1. Prepare a CSV file with one row per region and one column per indicator.
2. Copy `data/config_pakistan2022.json` and edit: the file name, the column of each indicator, its type and weight, and the indicators active in each stage.
3. Run

   ```bash
   python code/dcfss_tool.py --config data/my_event.json --out my_report
   python code/dcfss_tool.py --config data/my_event.json --tolerance 0.15 --out my_report
   ```

4. Open `my_report/priority_report.md`. It lists, for each stage, rank, region, index, band and tier, and a robustness note naming any adjacent regions whose order would change within the tolerance. `stage_<id>.csv` files contain the same information for further use.

## Daily use during an emergency

Replace the data with each new situation report and regenerate the report. Keep the weights and stage definitions fixed during an event so that changes in the ranking reflect changes in the data.
