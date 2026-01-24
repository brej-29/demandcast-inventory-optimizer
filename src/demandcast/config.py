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
    """Top-level application configuration."""
    debug: bool = False


@dataclass
class DataConfig:
    """Configuration related to data locations and defaults."""
    competition_slug: str = "demand-forecasting-kernels-only"
    raw_data_dir: Path = RAW_DATA_DIR
    processed_data_dir: Path = PROCESSED_DATA_DIR
    date_column: str = "date"
    item_column: str = "item"
    store_column: str = "store"
    target_column: str = "sales"


@dataclass
class ModelConfig:
    """Configuration for model training defaults (placeholders)."""
    default_horizon_days: int = 90
    frequency: str = "D"  # Daily data
    seed: int = 42


@dataclass
class InventoryConfig:
    """Configuration for inventory-related defaults (placeholders)."""
    default_service_level: float = 0.95
    default_lead_time_days: int = 7


@dataclass
class ArtifactConfig:
    """Configuration for model and report artifact locations."""
    artifacts_dir: Path = ARTIFACTS_DIR
    models_dir: Path = MODELS_DIR
    reports_dir: Path = REPORTS_DIR


app_config = AppConfig()
data_config = DataConfig()
model_config = ModelConfig()
inventory_config = InventoryConfig()
artifact_config = ArtifactConfig()