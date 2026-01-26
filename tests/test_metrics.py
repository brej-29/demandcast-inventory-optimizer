import numpy as np

from demandcast.evaluation.metrics import (
    coverage_fraction,
    mae,
    mape,
    mean_interval_width,
    rmse,
    smape,
    wape,
)


def test_metrics_basic_values() -> None:
    y_true = [10, 20, 30]
    y_pred = [12, 18, 33]

    assert rmse(y_true, y_pred) > 0
    assert mae(y_true, y_pred) > 0
    assert mape(y_true, y_pred) > 0
    assert smape(y_true, y_pred) > 0
    assert wape(y_true, y_pred) > 0


def test_metrics_handle_zero_demand() -> None:
    y_true = [0, 0, 0]
    y_pred = [0, 1, 2]

    # WAPE should not explode when total demand is zero.
    assert wape(y_true, y_pred) == 0.0


def test_interval_metrics() -> None:
    y_true = [10, 20, 30]
    lower = [9, 19, 28]
    upper = [11, 21, 32]

    cov = coverage_fraction(y_true, lower, upper)
    width = mean_interval_width(lower, upper)

    assert 0 <= cov <= 1
    assert width > 0