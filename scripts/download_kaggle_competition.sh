#!/usr/bin/env bash
set -u

COMPETITION="demand-forecasting-kernels-only"
DATA_DIR="data/raw"

echo "DemandCast: Kaggle competition download helper"
echo "Competition: ${COMPETITION}"
echo

# Ensure kaggle CLI is available
if ! command -v kaggle >/dev/null 2>&1; then
  echo "Error: Kaggle CLI is not installed or not on PATH."
  echo "Install it via:"
  echo "  pip install kaggle"
  echo "Then configure your API token as described at:"
  echo "  https://github.com/Kaggle/kaggle-api#api-credentials"
  exit 1
fi

mkdir -p "${DATA_DIR}"

echo "Downloading competition files into ${DATA_DIR} ..."
if ! kaggle competitions download -c "${COMPETITION}" -p "${DATA_DIR}"; then
  echo "Error: kaggle CLI download command failed."
  echo "Please verify:"
  echo "  - Your network connection"
  echo "  - Your Kaggle API token (kaggle.json) is configured locally"
  exit 1
fi

# Check for unzip availability
if ! command -v unzip >/dev/null 2>&1; then
  echo "Download completed, but 'unzip' is not available."
  echo "Please install 'unzip' (e.g. 'sudo apt-get install unzip') and"
  echo "manually extract the zip file(s) in ${DATA_DIR}."
  exit 0
fi

echo "Extracting files ..."
for zip_file in "${DATA_DIR}"/*.zip; do
  if [ -f "${zip_file}" ]; then
    echo "  Unzipping ${zip_file}"
    unzip -o "${zip_file}" -d "${DATA_DIR}"
  fi
done

echo
echo "Contents of ${DATA_DIR}:"
ls -lh "${DATA_DIR}"

echo
echo "Kaggle competition download completed."