# Notebooks

This folder contains exploratory and analysis notebooks for the DemandCast project.

- `00_eda_template.ipynb` is a starter notebook for exploratory data analysis (EDA)
  on the Kaggle *Store Item Demand Forecasting Challenge* dataset.

Guidelines:

- Keep notebooks focused and well-documented.
- Avoid committing large output cells, intermediate data, or model artifacts.
- Prefer moving reusable logic into the `src/demandcast/` package and calling it
  from notebooks instead of duplicating code here.