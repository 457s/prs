$ErrorActionPreference = 'stop'

# 初始化PROFILE
(Get-Content $PSScriptRoot\profile.ps1 | ForEach-Object { $_.Replace('ROOT', $PSScriptRoot) } ) > $PROFILE

# 输出config.json
$config = Import-PowerShellDataFile -Path $PSScriptRoot\env\config.psd1
$config | ConvertTo-Json -Depth 20 | Out-File -FilePath $PSScriptRoot\env\config.json -Encoding utf8

# 脱敏输出init.txt
$clear_config = @{}
foreach ($kv in $config.getenumerator()) { $clear_config[$kv.key] = $kv.value.gettype().name }
$clear_config.GetEnumerator() | ForEach-Object { $out = "" } { $out += "`"$($_.key)`"=`"$($_.value)`"`n" }
"
# check path of prs with like ~\swq\prs
# shell version is pwsh 7
# python version is 3.11
# copy the context to `"env\config.psd1`" and input value

@{`n$out}
" `
    > $PSScriptRoot\init.txt

# 退出状态
Write-Host '>_'
