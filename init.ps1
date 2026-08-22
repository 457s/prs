$ErrorActionPreference = 'stop'

# 初始化PROFILE
(Get-Content $PSScriptRoot\env\profile.ps1 | ForEach-Object { $_.Replace('ROOT', $PSScriptRoot) } ) > $PROFILE

# 输出config.json
$config = Import-PowerShellDataFile -Path $PSScriptRoot\env\config.psd1
$config | ConvertTo-Json -Depth 20 | Out-File -FilePath $PSScriptRoot\env\config.json -Encoding utf8

# 配置python环境
Set-Location $PSScriptRoot\ai\
if (Test-Path .\.venv) {}else {
    python -m venv .venv;
    $ErrorActionPreference = 'continue'
    & .\.venv\scripts\pip.exe install -r requirements.txt
    $ErrorActionPreference = 'stop'
}
Set-Location $PSScriptRoot\mine\
if (Test-Path .\.venv) {}else {
    python -m venv .venv;
    $ErrorActionPreference = 'continue'
    & .\.venv\scripts\pip.exe install -r requirements.txt
    $ErrorActionPreference = 'stop'
}

# 脱敏输出init.txt
$clear_config = @{}
foreach ($kv in $config.getenumerator()) { $clear_config[$kv.key] = $kv.value.gettype().name }
$clear_config.GetEnumerator() | ForEach-Object { $out = "" } { $out += "`"$($_.key)`"=`"$($_.value)`"`n" }
"<# following these steps:
1.check the path of prs with like ~\swq\prs
2.check the version of pwsh is 7.
3.check the version of python is 3.11
4.copy all the context to `"env\config.psd1`" and input the values of hash table
5.execute the file as init.ps1
#>

@{`n$out}
" `
    > $PSScriptRoot\init.txt

# 退出状态
Write-Host "`n  >_" -ForegroundColor Yellow
exit 0
