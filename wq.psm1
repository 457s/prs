function wq_help {
    param(
        [string]$name
    )
    if ($name ) {
        if ($name -match '_') { Get-Help $name -Full }else { Get-Help "wq_$name" -Full }
    }
    else { Get-Command -Module wq ; Get-Alias | Where-Object { $_.Source -eq 'wq' } }
}
Set-Alias -Name wq_hl -Value wq_help


function wq_home {
    Set-Location ~\swq\prs
    try { & .\.venv\scripts\activate.ps1 }catch {}
}
Set-Alias -Name wq_hm -Value wq_home

function wq_mine {
    Set-Location ~\swq\prs\mine
    try { & .\.venv\scripts\activate.ps1 }catch {}
}
Set-Alias -Name wq_mi -Value wq_mine

function wq_ai {
    Set-Location ~\swq\prs\ai
    try { & .\.venv\scripts\activate.ps1 }catch {}
}



function wq_homespace {
    wq_home; Get-ChildItem -File | Where-Object { $_.Extension -eq '.code-workspace' } | ForEach-Object { explorer.exe $_.FullName }
}
Set-Alias -Name wq_hms -Value wq_homespace

function wq_minespace {
    wq_mine; Get-ChildItem -File | Where-Object { $_.Extension -eq '.code-workspace' } | ForEach-Object { explorer.exe $_.FullName }
}
Set-Alias -Name wq_mis -Value wq_minespace

function wq_aispace {
    wq_ai; Get-ChildItem -File | Where-Object { $_.Extension -eq '.code-workspace' } | ForEach-Object { explorer.exe $_.FullName }
}
Set-Alias -Name wq_ais -Value wq_aispace

function wq_main {
    python .\main.py
}
Set-Alias -Name wq_m -Value wq_main


function wq_minemain {
    wq_mine; wq_main
}
Set-Alias -Name wq_mim -Value wq_minemain



function wq_aimain {
    wq_ai; wq_main
}
Set-Alias -Name wq_aim -Value wq_aimain


function wq_clear {
    param (
        [string[]]$strings
    )
    $strings | foreach-object { [int]$_.replace(',', '').replace('，', '').replace('￥', '').replace(' ', '') }
}
Set-Alias -Name wq_cl -Value wq_clear


function wq_checkvenv {
    $check = Get-ChildItem env: | Where-Object { $_.name -like '*venv*' -or $_.value -like '*venv*' }
    if ($check) { Write-Host "(venv status)" -ForegroundColor Yellow; $check }else { Write-Host "(venv status is null)" -ForegroundColor Yellow }
}
Set-Alias -Name wq_cv -Value wq_checkvenv


function wq_restart {
    Start-Process pwsh -NoNewWindow -UseNewEnvironment -ArgumentList '-noexit', '-command', "write-host;wq_checkvenv"
    [System.Environment]::Exit(0)
}
Set-Alias -Name wq_rs -Value wq_restart





function wq_qwen {
    ollama list | ForEach-Object { $_.Split(' ')[0] } | Select-Object -Skip 1 | ForEach-Object { $module = @{}; $c = 0 } { $c++; $module["id_$c"] = $_ } { $module } 
    $id = Read-Host "input module id"
    Write-Host "`n>$($module["id_$id"])<"
    ollama run $module["id_$id"]
}
Set-Alias -Name wq_qw -Value wq_qwen


function wq_aiwork {
    <#
    .PARAMETER n
        文件夹名称
    .PARAMETER d
        任务描述
    .PARAMETER file_paths
        打包参数
    #>
    param(
        [string]$n,
        [string]$d,
        [Parameter(ValueFromRemainingArguments = $true)]    
        [string[]]$file_paths
    )
    if ($n -ne 't') {
        $dest_folder_name = $n
    }
    else { $dest_folder_name = Get-Date -Format "yy年MM月dd日HH时mm分ss秒" }
    if ($file_paths) {
        $dest_folder_path_old = Join-Path $PSScriptRoot "ai\works\$dest_folder_name"
        if (Test-Path $dest_folder_path_old) { $c = 0; $e = '!'; do { $c++; $dest_folder_path = $dest_folder_path_old + ($e * $c) }while (Test-Path $dest_folder_path) }
        else { $dest_folder_path = $dest_folder_path_old }
        New-Item -ItemType Directory -Path $dest_folder_path
        $content = "在此目录下展开工作：$dest_folder_path`n$d"
        New-Item -ItemType File -Path (Join-Path $dest_folder_path 'description.txt') | Set-Content -Value $content
        $file_paths | ForEach-Object { $file_name = Split-Path $_ -Leaf ; 
            if (-not (Test-Path (Join-Path $dest_folder_path $file_name))) { Copy-Item -Path $_ -Destination $dest_folder_path }else {
                $c = 0; $e = '!' ; do { $c++; $file_path = Join-Path $dest_folder_path (($e * $c) + $file_name) }while (Test-Path $file_path);
                Copy-Item -Path $_ -Destination  $file_path 
            } }
        wq_aispace
    }
    else { Write-Host 'please input the paths of files you want to copy' }
}
Set-Alias -Name wq_aiw -Value wq_aiwork



function wq_init {
    & $PSScriptRoot\init.ps1
}
Set-Alias -Name wq_it -Value wq_init

function wq_gt {
    wq_home; git status
}

