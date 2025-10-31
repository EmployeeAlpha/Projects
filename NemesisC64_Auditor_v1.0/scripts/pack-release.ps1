<#
    NemesisC64 Auditor — pack-release.ps1
    Creates a clean zip archive of the latest build for release or backup.
#>

param(
    [string]$Configuration = "Release",
    [string]$Runtime = "win-x64"
)

Write-Host "=== NemesisC64 Auditor: Packaging Script ==="
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Repo = Split-Path -Parent $Root
$Project = Join-Path $Repo "src\WpfApp"
$PublishDir = Join-Path $Repo "publish"
$OutDir = Join-Path $PublishDir "NemesisC64_Auditor_v1.0"

# Clean old publish dir
if (Test-Path $PublishDir) { Remove-Item $PublishDir -Recurse -Force }
New-Item -ItemType Directory -Path $PublishDir | Out-Null

# Build and publish
Write-Host "Publishing project..."
dotnet publish "$Project" -c $Configuration -r $Runtime --self-contained true -p:PublishSingleFile=false -o $OutDir

# Verify output
if (!(Test-Path (Join-Path $OutDir "NemesisC64.Auditor.exe"))) {
    Write-Host "❌ Publish failed or executable not found."
    exit 1
}

# Clean up reports/logs to avoid bundling user data
Write-Host "Cleaning reports and logs..."
Get-ChildItem (Join-Path $OutDir "reports") -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem (Join-Path $OutDir "logs") -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Zip it
$Date = Get-Date -Format "yyyyMMdd_HHmmss"
$ZipName = "NemesisC64_Auditor_${Date}.zip"
$ZipPath = Join-Path $PublishDir $ZipName

Write-Host "Creating archive..."
Compress-Archive -Path "$OutDir\*" -DestinationPath $ZipPath -Force

Write-Host "`n✅ Packaging complete!"
Write-Host "Output: $ZipPath"
