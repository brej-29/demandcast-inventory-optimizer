import pandas as pd

from demandcast.data.synthetic import generate_demo_series
from demandcast.models import LGBMForecaster


def test_lgbm_forecaster_basic_shapes() -> None:
    series_df = generate_demo_series()
    series_df = series_df[["ds", "y"]].copy()

    model = LGBMForecaster()
    model.fit(series_df)

    horizon = 14
    last_ds = series_df["ds"].max()
    future_ds = pd.date_range(start=last_ds + pd.Timedelta(days=1), periods=horizon, freq="D")
    future_df = pd.DataFrame({"ds": future_ds})

    preds = model.predict(future_df, horizon=horizon)

    assert len(preds) == horizon
    assert set(["ds", "yhat", "yhat_lower", "yhat_upper"]).issubset(preds.columns)
    assert preds["yhat"].isna().sum() == 0