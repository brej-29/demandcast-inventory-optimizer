import numpy as np
import pandas as pd

from demandcast.data.synthetic import generate_demo_series
from demandcast.models import EnsembleConfig, EnsembleForecaster


def test_ensemble_weights_normalization() -> None:
    cfg = EnsembleConfig(weights={"sarimax": 1.0, "ets": 2.0, "lgbm": 0.0})
    ens = EnsembleForecaster(config=cfg)
    normalized = ens.normalize_weights(cfg.weights)
    assert abs(sum(normalized.values()) - 1.0) < 1e-6
    assert all(v >= 0.0 for v in normalized.values())


def test_ensemble_prediction_interval_conservative_includes_mean() -> None:
    series_df = generate_demo_series()
    series_df = series_df[["ds", "y"]].copy()

    cfg = EnsembleConfig()
    ens = EnsembleForecaster(config=cfg)
    ens.fit(series_df)

    last_ds = series_df["ds"].max()
    horizon = 7
    future_ds = pd.date_range(start=last_ds + pd.Timedelta(days=1), periods=horizon, freq="D")
    future_df = pd.DataFrame({"ds": future_ds})

    preds = ens.predict(future_df, horizon=horizon)

    assert len(preds) == horizon
    assert set(["ds", "yhat", "yhat_lower", "yhat_upper"]).issubset(preds.columns)

    yhat = preds["yhat"].to_numpy()
    lower = preds["yhat_lower"].to_numpy()
    upper = preds["yhat_upper"].to_numpy()

    assert np.all(lower <= yhat)
    assert np.all(upper >= yhat)