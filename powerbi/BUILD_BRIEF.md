# Power BI project: AI Data-Centre Water Dashboard

A first Power BI project built on your own AI Water Tracker data. It closes the BI
skill gap and stands as a portfolio piece a hiring manager has not seen before: a
water-stress map of AI data centres with a measured-versus-planning-only flag.

Data: `ai_water_sites.csv` (10 sites, derived from `sites.csv`).

## One project, two layers (SQL then BI)
This is a single pipeline, the way real analyst work flows: shape in SQL, present in BI.
- **SQL layer (`queries.sql`, DuckDB):** filtering, grouping, ranking and the
  measured-versus-planning split, run locally on your Linux box with no server.
- **BI layer (this brief, Power BI):** the same data and splits made visual (map, KPI
  cards, matrix).
It reads as one portfolio story ("AI data-centre water: SQL analysis feeding a Power BI
dashboard") while giving you two separate CV skill lines, SQL and Power BI. Run the SQL
first to understand the data, then build the visuals.

## 0. Platform — DECIDED: Windows 11 VM (2026-07-16)
Power BI Desktop is Windows-only and will not run on Fedora atomic. Chosen route: a
Windows 11 VM on this box. The machine is well over the bar (KVM on, 56 cores, 62 GB
RAM), so an 8 GB / 4-CPU VM runs comfortably alongside local Qwen.

Setup, shortest path:
1. Install GNOME Boxes (Flatpak, no reboot, no rpm-ostree layering):
   `flatpak install flathub org.gnome.Boxes`
2. Download the Windows 11 ISO from Microsoft. In Boxes: New > select the ISO. Boxes
   configures the virtual TPM and Secure Boot that Win11 requires; give it ~8 GB RAM,
   4 CPUs, 64 GB disk.
3. Inside Windows, install Power BI Desktop (standalone installer from Microsoft; no
   account needed to author locally and save a .pbix).
4. Get the data in with no file-sharing faff: the CSV is public now, so in the VM's
   browser download `ai_water_sites.csv` straight from the repo
   (github.com/NMAIResearch/ai-water-tracker/tree/main/powerbi), then follow section 1.
5. Out: save the .pbix and screenshots. A public link is optional via Power BI Service
   "Publish to web" (needs a free work/school-style account).
If Boxes struggles with the Win11 TPM step, fall back to layering virt-manager + swtpm
(`rpm-ostree install virt-manager swtpm libvirt`, then reboot), which gives an explicit vTPM.

Your method holds: an AI assistant can generate any DAX or Power Query step; you place
and verify it. This brief gives you every measure so nothing is guesswork.

## 1. Load the data
1. Get Data > Text/CSV > `ai_water_sites.csv` > Transform Data.
2. In Power Query, set types: WaterDemand_ML_d, Capacity_ML_d, WCI, WUE_L_per_kWh,
   EWIF_lo, EWIF_hi = Decimal Number; everything else = Text.
3. Confirm City, State, Country, Location are Text (needed for the map to geocode).
4. Close & Apply. One table is fine here; a star schema is overkill for 10 rows, note
   in your write-up that you would split Operator and Site into dimensions if it grew.

## 2. Measures (DAX) — paste each as a New Measure
```
Total Sites = COUNTROWS('ai_water_sites')
Operators = DISTINCTCOUNT('ai_water_sites'[Operator])
Primary Verified = CALCULATE([Total Sites], 'ai_water_sites'[Status] = "Primary-verified")
Planning Only = CALCULATE([Total Sites], 'ai_water_sites'[Status] = "Planning only (not operational)")
% Primary Verified = DIVIDE([Primary Verified], [Total Sites])
Avg WCI = AVERAGE('ai_water_sites'[WCI])
Total Water Demand (ML/d) = SUM('ai_water_sites'[WaterDemand_ML_d])
Hydro-Coupled Sites = CALCULATE([Total Sites], 'ai_water_sites'[HydroCoupled] = "Yes")
```
Set `% Primary Verified` format to Percentage (1 dp).

## 3. Visuals (page layout, top to bottom)
1. **Title text box:** "AI Data-Centre Water Dashboard" + one line: "Site-level water
   consumption index for AI data centres, flagged by verification status. Source: AI
   Water Tracker (DOI 10.5281/zenodo.21318960)."
2. **KPI cards (row of five):** Total Sites, % Primary Verified, Planning Only,
   Avg WCI, Total Water Demand (ML/d).
3. **Map (the centrepiece):** use the Map visual.
   - Location = `Location` field.
   - Bubble size = `WaterDemand_ML_d`.
   - Legend = `Status` (so planning-only sites read as a different colour).
4. **Clustered bar chart:** Axis = `Operator` + `City`; Value = `WCI`; Legend = `Cooling`.
   Title: "Water consumption index by site".
5. **Matrix:** Rows = `Operator`; Columns = `Status`; Values = Total Sites. Shows the
   measured-vs-planning split per operator at a glance.
6. **Slicers (down the left):** Operator, Cooling, Status, GridRegion, HydroCoupled.

Optional scatter: X = Capacity_ML_d, Y = WaterDemand_ML_d, size = WCI, legend = Operator.

## 4. Style (matches your house palette)
Navy `#1a365d` as the primary, slate text `#2d3748`, light background `#f7fafc`.
View > Themes > Customise current theme, set those. Keep it plain: no drop shadows,
titles left-aligned, one accent colour.

## 5. Ship it (for the portfolio)
- File > Export > PDF for a static copy to attach to applications.
- Or Publish to the Power BI Service and share a view link (work/school account only).
- Or a clean screenshot for the CV / GitHub Pages.
- Add a line to the CV skills block once done: "Power BI: interactive dashboard over a
  published dataset (map, KPI cards, DAX measures)."

## 6. Interview talking points (why this beats a sales-dashboard demo)
- You modelled a real, sourced dataset, not a toy.
- The `Status` flag is a data-quality/governance decision: two of ten widely cited
  "sites" are non-operational planning figures, and the dashboard refuses to plot them
  as measured. That is the analyst judgement, made visible.
- The DAX measures separate a count from a rate (denominator discipline), the same
  habit your written work is built on.
```
```
