# Breast Cancer Cohort Explorer

An interactive Streamlit dashboard for the exploratory analysis in `EDA/breast_cancer.ipynb`. It includes linked filters, interactive charts, cohort summaries, a filtered-record download, and a data-quality view.

## Run the dashboard

From this project folder in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Or double-click `run_dashboard.bat`.

To recreate the environment:

```powershell
uv venv .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
```

If `uv` is not installed, create the environment with `python -m venv .venv`, then run `\.venv\Scripts\python.exe -m pip install -r requirements.txt`.

## Dashboard sections

- **Overview:** cohort size, recorded vital-status share, observed-month and tumor-size medians, stage distribution, age, and tumor-size distributions.
- **Tumor & nodes:** tumor size against positive regional nodes, node summaries, and recorded status by stage.
- **Status & receptors:** recorded months by status and descriptive receptor-group comparisons.
- **Demographics:** age, race, and marital-status distributions.
- **Records & quality:** filtered source fields, missing-cell count, field guide, and CSV export.

The sidebar filters age, tumor size, vital status, sixth-edition stage, race, and both receptor fields. Expand **More clinical & demographic filters** for T/N/summary stage, grade, differentiation, and marital status. Upload a CSV with the notebook's 16 fields to explore another copy of the cohort.

## Data and interpretation

The notebook points to `/content/Breast_Cancer.csv`, which was not included in the project. The dashboard bundles a public SEER-derived cohort shared on [Zenodo, record 5120960](https://zenodo.org/records/5120960), originally credited there to Jing Teng / IEEE DataPort (DOI: 10.21227/a9qy-ph35). This published CSV has an extra blank column and combines differentiation with grade; the dashboard maps it into the notebook's 16-field schema and exports those fields.

These are historical records for patients diagnosed in 2006-2010. The notebook performs descriptive exploration only. "Alive" is a recorded status at the dataset endpoint, and its associated months can be right-censored follow-up. Charts show unadjusted descriptions, not population-level survival estimates, causal effects, or individual prognosis. Tumor-size units are not specified in the notebook, so the dashboard keeps the source units unnamed.
