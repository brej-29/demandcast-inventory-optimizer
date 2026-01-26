# Project Goal

Build **DemandCast**, a production-quality, free-to-deploy workflow for:

- Forecasting store-item level demand using the Kaggle competition  
  *Store Item Demand Forecasting Challenge* (`demand-forecasting-kernels-only`).
- Translating forecasts into **inventory decisions** (e.g., reorder points, safety
  stock, and order quantities).
- Surfacing insights and controls through a **Streamlit dashboard** that can be
  run locally or hosted on a free platform (subject to provider limits).

The initial milestones are:

1. Reliable, repeatable data ingestion from Kaggle into `data/raw/`.
2. Clear experiment and EDA workflows (via notebooks and scripts).
3. A modular Python package (`src/demandcast/`) that separates data handling,
   feature engineering, models, inventory logic, and evaluation.
4. A Streamlit app (`app/`) that exposes forecasts, backtests, and inventory
   recommendations through simple, robust pages.

The overarching aim is to have a **learnable, maintainable reference project**
that demonstrates good engineering practices around time series forecasting and
inventory optimization, not just a single competition submission.