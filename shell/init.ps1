$ErrorActionPreference = 'stop'

# 初始化
$config = Import-PowerShellDataFile -Path $PSScriptRoot\env\config.psd1
(Get-Content $PSScriptRoot\profile.ps1 | ForEach-Object { $_.Replace('ROOT', $config["ROOT"]) } ) > $PROFILE
$config | ConvertTo-Json -Depth 20 | Out-File -FilePath $PSScriptRoot\env\config.json -Encoding utf8


# 脱敏输出init.txt
$clear_config = @{}
foreach ($kv in $config.getenumerator()) {
    $clear_config[$kv.key] = 
    if ($kv.key -eq 'ROOT') { $kv.value }
    else { $kv.value.gettype().name } 
}
$clear_config.GetEnumerator() | ForEach-Object { $out = "" } { $out += "`"$($_.key)`"=`"$($_.value)`"`n" }
"# copy to `"env\config.psd1`" and input value`n# keep structure of ROOT with like ~\swq\prs`n`n@{`n$out}`n" > $PSScriptRoot\init.txt


# 退出状态
Write-Host '>_'

