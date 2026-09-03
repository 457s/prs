$ErrorActionPreference = 'stop'
$ROOT = Split-Path(Split-Path $PSScriptRoot -Parent) -Parent

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
