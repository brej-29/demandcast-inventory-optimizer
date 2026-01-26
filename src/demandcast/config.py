import os
from dataclasses import dataclass
from pathlib import Path

from .paths import (
    ARTIFACTS_DIR,
    MODELS_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    REPORTS_DIR,
)


@dataclass
class AppConfig:
    debug: bool = False


@dataclass
class DataConfig:
    competition_slug: str = "demand-forecasting-kernels-only"
    raw_data_dir: Path = RAW_DATA_DIR
    processed_data_dir: Path = PROCESSED_DATA_DIR
    raw_train_filename: str = "train.csv"
    date_column: str = "date"
    item_column: str = "item"
    store_column: str = "store"
    target_column: str = "sales"
    default_series_mode: str = "single_sku"
    default_store_id: int = 1
    default_item_id: int = 1
    resample_freq: str = "D"
    processed_series_filename: str = "series_default.parquet"

    @property
    def allowed_series_modes(self) -> tuple[str, ...]:
        return ("single_sku", "aggregate_items", "aggregate_stores", "total")


@dataclass
class ModelConfig:
    forecast_horizon_days: int = 90
    frequency: str = "D"
    seed: int = 42


@dataclass
class BacktestConfig:
    initial_train_days: int = 365 * 2
    step_days: int = 30
    n_folds: int = 6


@dataclass
class InventoryConfig:
    default_service_level: float = 0.95
    default_lead_time_days: int = 7
    holding_cost_pct: float = 0.2
    ordering_cost: float = 1.0


@dataclass
class ArtifactConfig:
    artifacts_dir: Path = ARTIFACTS_DIR
    models_dir: Path = MODELS_DIR
    reports_dir: Path = REPORTS_DIR


app_config = AppConfig()
data_config = DataConfig()
model_config = ModelConfig()
backtest_config = BacktestConfig()
inventory_config = InventoryConfig()
artifact_config = ArtifactConfig()

DATA_RAW_DIR: Path = data_config.raw_data_dir
DATA_PROCESSED_DIR: Path = data_config.processed_data_dir
ARTIFACTS_DIR: Path = artifact_config.artifacts_dir

KAGGLE_COMPETITION: str = data_config.competition_slug
RAW_TRAIN_FILENAME: str = data_config.raw_train_filename
DEFAULT_SERIES_MODE: str = data_config.default_series_mode
DEFAULT_STORE_ID: int = data_config.default_store_id
DEFAULT_ITEM_ID: int = data_config.default_item_id
RESAMPLE_FREQ: str = data_config.resample_freq

FORECAST_HORIZON_DAYS: int = model_config.forecast_horizon_days

METRIC_NAMES: list[str] = ["rmse", "mae", "mape", "smape", "wape"]

INVENTORY_DEFAULTS = {
    "lead_time_days": inventory_config.default_lead_time_days,
    "service_level": inventory_config.default_service_level,
    "holding_cost_pct": inventory_config.holding_cost_pct,
    "ordering_cost": inventory_config.ordering_cost,
}


def load_settings_from_env_or_defaults() -> dict:
    def _int_env(name: str, default: int) -> int:
        raw = os.getenv(name)
        if raw is None:
            return default
        try:
            return int(raw)
        except ValueError:
            return default

    series_mode = os.getenv("DEMANDCAST_SERIES_MODE", DEFAULT_SERIES_MODE)
    if series_mode not in data_config.allowed_series_modes:
        series_mode = DEFAULT_SERIES_MODE

    settings = {
        "series_mode": series_mode,
        "store_id": _int_env("DEMANDCAST_STORE_ID", DEFAULT_STORE_ID),
        "item_id": _int_env("DEMANDCAST_ITEM_ID", DEFAULT_ITEM_ID),
        "forecast_horizon_days": _int_env(
            "DEMANDCAST_FORECAST_HORIZON_DAYS",
            FORECAST_HORIZON_DAYS,
        ),
        "initial_train_days": _int_env(
            "DEMANDCAST_BACKTEST_INITIAL_TRAIN_DAYS",
            backtest_config.initial_train_days,
        ),
        "step_days": _int_env(
            "DEMANDCAST_BACKTEST_STEP_DAYS",
            backtest_config.step_days,
        ),
        "n_folds": _int_env(
            "DEMANDCAST_BACKTEST_N_FOLDS",
            backtest_config.n_folds,
        ),
    }
    return settings