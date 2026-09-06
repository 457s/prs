$ErrorActionPreference = 'stop'

Set-Location $PSScriptRoot
if (Test-Path .\.venv) {}else {
    python -m venv .venv;
    $ErrorActionPreference = 'continue'
    & .\.venv\scripts\pip.exe install -r requirements.txt
}
