# Deploying DemandCast to Hugging Face Spaces (Streamlit)

This document describes how to deploy the DemandCast dashboard to a free
**Hugging Face Streamlit Space**.

## Requirements

- A Hugging Face account.
- This repository accessible from the Space (public or via a fork).
- The Space type set to **Streamlit**.

The project is designed so that the Space can run entirely in **demo mode**
without access to Kaggle data.

## Files Hugging Face cares about

- `app.py` – root-level Streamlit entrypoint.
- `requirements.txt` – Python dependencies.

The Space runtime will roughly execute:

```bash
pip install -r requirements.txt
streamlit run app.py
```

No additional configuration is strictly required.

## Deployment steps

1. **Create a new Space**

   - Go to https://huggingface.co/spaces.
   - Click **New Space**.
   - Choose:
     - **Space SDK**: `Streamlit`
     - **Hardware**: the default CPU option
     - **Repository visibility**: as desired

2. **Point the Space at this repository**

   You have two main options:

   - **Fork this repo on GitHub** and select that fork when creating the Space.
   - Or **upload the files directly** into the Space’s Git repository.

3. **Verify the configuration**

   Ensure that:

   - `app.py` is at the root of the repo.
   - `requirements.txt` is present and contains all required libraries:
     - `streamlit`, `pandas`, `numpy`, `scikit-learn`, `statsmodels`,
       `matplotlib`, `plotly`, `lightgbm`, `mapie`, `prophet`.

4. **Wait for the Space to build**

   On first launch the Space will:

   - Install dependencies from `requirements.txt`.
   - Start the Streamlit server with `app.py`.

   This may take a few minutes, especially when compiling scientific libraries.

5. **Use the app in demo mode**

   The Space **does not need Kaggle data**:

   - When no processed series is found under `data/processed/`, the app
     automatically falls back to small demo assets under `assets/demo/` and
     `assets/demo_artifacts/`.
   - All pages (Overview, Forecast, Inventory, Backtests) are designed to
     handle missing artifacts gracefully and display instructions rather than
     crashing.

## Optional: advanced tweaks

If you need system-level packages (for example, certain compilers or
libraries), you can add a `packages.txt` file at the repo root. The HF
runtime will install those packages via `apt` before installing Python
dependencies.

In many cases, DemandCast works fine **without** any extra system packages,
so `packages.txt` can remain empty or be omitted entirely.

## Updating the Space

To deploy updates:

- Push changes to the branch the Space tracks (e.g. `main`).
- Or manually edit files in the Space’s repository on Hugging Face.

The Space will rebuild automatically on new commits.

## Troubleshooting

- **Import errors:** ensure all required libraries are listed in
  `requirements.txt`.
- **Long build times or timeouts:** consider trimming unused dependencies.
- **App errors:** check the Space logs; they often surface missing artifacts
  or configuration issues. The UI also shows actionable hints when key
  scripts have not been run.

For deeper details on architecture and metrics, see the main `README.md`
and the `context/` folder in the repository.