$ErrorActionPreference = 'stop'

Set-Location $PSScriptRoot
if (Test-Path .\.venv) { Write-Host '.venv is exists' -ForegroundColor Green }else {
    python -m venv .venv;
    $ErrorActionPreference = 'continue'
    & .\.venv\scripts\pip.exe install -r requirements.txt
}
