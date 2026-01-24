Param(
    [string]$CompetitionSlug = "demand-forecasting-kernels-only",
    [string]$DataDir = "data/raw"
)

Write-Host "DemandCast: Kaggle competition download helper"
Write-Host "Competition: $CompetitionSlug"
Write-Host ""

# Ensure kaggle CLI is available
if (-not (Get-Command kaggle -ErrorAction SilentlyContinue)) {
    Write-Error "Kaggle CLI is not installed or not on PATH."
    Write-Host "Install it via:"
    Write-Host "  pip install kaggle"
    Write-Host "Then configure your API token as described at:"
    Write-Host "  https://github.com/Kaggle/kaggle-api#api-credentials"
    exit 1
}

if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir | Out-Null
}

Write-Host "Downloading competition files into $DataDir ..."
kaggle competitions download -c $CompetitionSlug -p $DataDir
if ($LASTEXITCODE -ne 0) {
    Write-Error "kaggle CLI download command failed."
    Write-Host "Please verify:"
    Write-Host "  - Your network connection"
    Write-Host "  - Your Kaggle API token (kaggle.json) is configured locally"
    exit $LASTEXITCODE
}

$zipFiles = Get-ChildItem -Path $DataDir -Filter "*.zip" -ErrorAction SilentlyContinue
if (-not $zipFiles) {
    Write-Warning "No zip files found in $DataDir after download."
} else {
    foreach ($zip in $zipFiles) {
        Write-Host "Extracting $($zip.FullName) ..."
        try {
            Expand-Archive -Path $zip.FullName -DestinationPath $DataDir -Force
        } catch {
            Write-Warning "Failed to extract $($zip.Name): $_"
        }
    }
}

Write-Host ""
Write-Host "Contents of $DataDir:"
Get-ChildItem -Path $DataDir -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Kaggle competition download completed."
exit 0