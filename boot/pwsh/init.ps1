$ErrorActionPreference = 'stop'
$ROOT = Split-Path(Split-Path $PSScriptRoot -Parent) -Parent

# 初始化PROFILE
(Get-Content $ROOT\boot\pwsh\profile.ps1 | ForEach-Object { $_.Replace('ROOT', $ROOT) } ) > $PROFILE

# 退出状态
Write-Host ">_" -ForegroundColor Yellow
