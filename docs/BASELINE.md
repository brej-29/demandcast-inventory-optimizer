# Starting-state audit

Remote default branch: `main`. Pulled with `git pull --ff-only origin main`; already current at `d5db1f3` (January 26, 2026). Local backup tag: `backup/pre-rebuild-20261105`. History is preserved. No sibling application boundary was found in the entrypoints, package imports, or remote configuration; no other repository was modified.

## What worked

- Isolated Python 3.11 environment: `uv venv .venv --python 3.11` followed by `uv pip install --python .venv/Scripts/python.exe -r requirements.txt openpyxl` installed 66 packages. The tested versions are now frozen in `requirements-research.lock.txt`.
- `.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider`: **11 passed, 53 warnings**, 73.04 seconds. The warnings concern deprecated pandas APIs used by forecasting dependencies and feature code.
- `streamlit run app.py --server.headless true --server.port 8501` started successfully. `GET /_stcore/health` returned **200, ok**. This establishes startup, not complete behavior of every research page.

## What needed correction

- `src/demandcast/inventory/optimizer.py::_summarise_forecast` computes sample standard deviation of `yhat`. This measures shape of the point forecast, not uncertainty of actual demand. `python scripts/reproduce_legacy_failure.py` reproduces a zero safety buffer for a flat forecast despite volatile synthetic observations; machine-readable output is `docs/verification/legacy-counterexample.json`.
- The UI depends on previously produced files and can train expensive models during interactive use. Its multiple root/app entrypoints duplicate navigation; missing artifacts lead to instructions to run scripts rather than a complete first-time workflow.
- `assets/demo_artifacts/model_comparison.csv` is synthetic demo evidence: interval coverage 100% for ETS, 28.6% for the fallback, and 52.4% for LightGBM. Those are committed artifacts, not a new evaluation or evidence of real retailer performance.
- Deploy dependencies were unpinned. The first environment's `python` executable resolved into an unrelated project and had no pip; all installations were redirected into this repository's `.venv` without modifying that project.
- Old deployment instructions target a Streamlit Space workflow and do not provide a verified live URL. They are superseded by the static workbench and GitHub Pages workflow.

## What stays

The inventory decision problem, established name, Python forecasting research package, notebooks, and tests. The browser workbench is the public product. Archived research is not imported into the shipped application and does not need to run to use it.
