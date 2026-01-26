import importlib
import logging
import platform
import sys
from typing import List


def _configure_logging() -> logging.Logger:
    logger = logging.getLogger("demandcast.verify_env")
    if not logger.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
    return logger


logger = _configure_logging()


def _check_packages(packages: List[str]) -> None:
    for pkg in packages:
        try:
            module = importlib.import_module(pkg)
            version = getattr(module, "__version__", "unknown")
            print(f"{pkg}: {version}")
        except ImportError:
            logger.warning("Package %s is not installed", pkg)
            print(f"{pkg}: NOT INSTALLED")


def main() -> None:
    """
    Print basic environment information and dependency status.

    This script is intentionally tolerant: it logs missing packages but always
    exits with status code 0 so it can be used as a lightweight sanity check.
    """
    logger.info("Starting environment verification")

    print("DemandCast environment verification")
    print("------------------------------")
    print(f"Python executable: {sys.executable}")
    print(f"Python version   : {sys.version.split()[0]}")
    print(f"Platform         : {platform.platform()}")
    print()

    print("Checking core packages:")
    core_packages = [
        "streamlit",
        "pandas",
        "numpy",
        "sklearn",
        "statsmodels",
        "matplotlib",
        "plotly",
    ]
    _check_packages(core_packages)

    print()
    print("Checking optional packages (requirements-extra.txt):")
    optional_packages = [
        "prophet",
        "lightgbm",
        "mapie",
    ]
    _check_packages(optional_packages)

    logger.info("Environment verification completed")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Unexpected error during environment verification: %s", exc)
        print(
            f"Environment verification encountered an unexpected error: {exc}",
            file=sys.stderr,
        )
    finally:
        # Always exit with status code 0 as per project requirements.
        sys.exit(0)