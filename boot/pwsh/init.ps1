$ErrorActionPreference = 'stop'
$ROOT=Split-Path(Split-Path $PSScriptRoot -Parent) -Parent

# 初始化PROFILE
(Get-Content $ROOT\boot\pwsh\profile.ps1 | ForEach-Object { $_.Replace('ROOT', $ROOT) } ) > $PROFILE

# 配置python环境
Set-Location $Root\ai\
if (Test-Path .\.venv) {}else {
    python -m venv .venv;
    $ErrorActionPreference = 'continue'
    & .\.venv\scripts\pip.exe install -r requirements.txt
    $ErrorActionPreference = 'stop'
}
Set-Location $Root\mine\
if (Test-Path .\.venv) {}else {
    python -m venv .venv;
    $ErrorActionPreference = 'continue'
    & .\.venv\scripts\pip.exe install -r requirements.txt
    $ErrorActionPreference = 'stop'
}

# 退出状态
Write-Host ">_" -ForegroundColor Yellow
exit 0
