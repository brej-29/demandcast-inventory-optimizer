import pandas as pd

from demandcast.data.synthetic import generate_demo_series
from demandcast.models.prophet_fallback import ProphetFallbackModel, _PROPHET_AVAILABLE


def test_prophet_fallback_works_without_prophet() -> None:
    # Force fallback path even if prophet is installed.
    series_df = generate_demo_series()
    series_df = series_df[["ds", "y"]].copy()

    model = ProphetFallbackModel()
    model._use_prophet = False  # force SARIMAX backend
    model.fit(series_df)

    last_ds = series_df["ds"].max()
    horizon = 7
    future_ds = pd.date_range(start=last_ds + pd.Timedelta(days=1), periods=horizon, freq="D")
    future_df = pd.DataFrame({"ds": future_ds})

    preds = model.predict(future_df, horizon=horizon)
    assert len(preds) == horizon
    assert set(["ds", "yhat"]).issubset(preds.columns)