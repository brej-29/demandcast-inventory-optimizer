import pandas as pd

from demandcast.data.synthetic import generate_demo_series
from demandcast.evaluation import RollingBacktestSettings, backtest_model_class
from demandcast.models import ARIMASARIMAXModel


def test_backtest_output_shapes() -> None:
    series_df = generate_demo_series()
    series_df = series_df[["ds", "y"]].copy()

    settings = RollingBacktestSettings(
        initial_train_days=60,
        step_days=14,
        horizon_days=7,
        n_folds=3,
    )

    preds_df, agg_metrics, fold_results = backtest_model_class(
        series_df, ARIMASARIMAXModel, settings
    )

    assert not preds_df.empty
    assert set(["ds", "y", "yhat"]).issubset(preds_df.columns)
    assert len(fold_results) >= 1
    assert "rmse" in agg_metrics