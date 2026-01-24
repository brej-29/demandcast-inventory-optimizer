# Dataset: Store Item Demand Forecasting Challenge

This project uses the Kaggle competition:

- **Name:** Store Item Demand Forecasting Challenge  
- **Slug:** `demand-forecasting-kernels-only`  
- **URL:** https://www.kaggle.com/c/demand-forecasting-kernels-only

The dataset contains daily sales for multiple stores and items, which makes it
well-suited for exploring store-item level demand forecasting and downstream
inventory optimization.

---

## How we download the data

Data is downloaded via the **Kaggle CLI** directly into the `data/raw/`
directory in this repository.

From the project root, run:

```bash
kaggle competitions download -c demand-forecasting-kernels-only -p data/raw
```

Alternatively, you can use the provided helper scripts:

- Bash (macOS/Linux/WSL/Git Bash):

  ```bash
  bash scripts/download_kaggle_competition.sh
  ```

- PowerShell (Windows):

  ```powershell
  pwsh scripts/download_kaggle_competition.ps1
  # or
  powershell -ExecutionPolicy Bypass -File scripts/download_kaggle_competition.ps1
  ```

These scripts:

- Validate that the `kaggle` CLI is available.
- Download the competition zip(s) into `data/raw/`.
- Extract the files into `data/raw/`.
- Print a summary of the resulting files.
- Fail gracefully with clear messages if something goes wrong.

---

## Kaggle API token setup (kaggle.json)

To use the Kaggle CLI, you must configure an API token on your local machine.

1. Sign in to Kaggle and go to your **Account** settings.
2. Under **API**, click **Create New API Token**.
3. This downloads a file named `kaggle.json`.

Place `kaggle.json` in one of the standard locations:

- macOS / Linux: `~/.kaggle/kaggle.json`
- Windows: `C:\Users\<USERNAME>\.kaggle\kaggle.json`

Ensure the file has restricted permissions (for example, `chmod 600` on Unix-like systems).

> **Important:** `kaggle.json` must be stored locally and must **never** be
> committed to this repository. The root `.gitignore` explicitly ignores
> `kaggle.json` and the `.kaggle/` directory.

If you prefer, you can also configure the path to `kaggle.json` via the
`KAGGLE_CONFIG_DIR` environment variable as described in the Kaggle API
documentation.