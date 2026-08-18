$ErrorActionPreference = 'stop'

# 初始化PROFILE
(Get-Content $PSScriptRoot\env\profile.ps1 | ForEach-Object { $_.Replace('ROOT', $PSScriptRoot) } ) > $PROFILE

# 输出config.json
$config = Import-PowerShellDataFile -Path $PSScriptRoot\env\config.psd1
$config | ConvertTo-Json -Depth 20 | Out-File -FilePath $PSScriptRoot\env\config.json -Encoding utf8

# 脱敏输出init.txt
$clear_config = @{}
foreach ($kv in $config.getenumerator()) { $clear_config[$kv.key] = $kv.value.gettype().name }
$clear_config.GetEnumerator() | ForEach-Object { $out = "" } { $out += "`"$($_.key)`"=`"$($_.value)`"`n" }
"<# following these step:
1.check path of prs with like ~\swq\prs
2.check pwsh version is 7.
3.check python version is 3.11
4.copy the context to `"env\config.psd1`" and input value
5.execute the file as init.ps1
6.make venv of pr and install with pip.txt
#>

@{`n$out}
" `
    > $PSScriptRoot\init.txt

# 退出状态
Write-Host '>_'
