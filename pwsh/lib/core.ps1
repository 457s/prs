function hl {
    param(
        [string]$name
    )
    if (-not $name) {
        Get-Content $HOME\core\prs\pwsh\lib\core.ps1 |
        ForEach-Object { [regex]::Match($_, "^function(.+){$").Groups[1].Value } | Where-Object { $_ } | Sort-Object
    }
    else {
        Write-Host $name -ForegroundColor Yellow
        (Get-Command $name).Definition
    }
}

function pr {
    Set-Location $HOME\core\prs
    try { & .\.venv\scripts\activate.ps1 }catch {}
}

function me {
    Set-Location $HOME\core\prs\ofme
    try { & .\.venv\scripts\activate.ps1 }catch {}
}

function ai {
    Set-Location $HOME\core\prs\ofai
    try { & .\.venv\scripts\activate.ps1 }catch {}
}

function prs {
    pr; Get-ChildItem -File | Where-Object { $_.Extension -eq '.code-workspace' } | ForEach-Object { explorer.exe $_.FullName }
}

function mes {
    me; Get-ChildItem -File | Where-Object { $_.Extension -eq '.code-workspace' } | ForEach-Object { explorer.exe $_.FullName }
}

function ais {
    ai; Get-ChildItem -File | Where-Object { $_.Extension -eq '.code-workspace' } | ForEach-Object { explorer.exe $_.FullName }
}

function pm {
    python .\main.py
}

function mem {
    me; pm
}

function aim {
    ai; pm
}

function cv {
    $check = Get-ChildItem env: | Where-Object { $_.name -like '*venv*' -or $_.value -like '*venv*' }
    if ($check) { Write-Host "(venv status)" -ForegroundColor Yellow; $check }else { Write-Host "(venv status is null)" -ForegroundColor Yellow }
}

function rs {
    Start-Process pwsh -NoNewWindow -UseNewEnvironment -ArgumentList '-noexit', '-command', "write-host;pws cv"
    [System.Environment]::Exit(0)
}

function qw {
    ollama list | ForEach-Object { $_.Split(' ')[0] } | Select-Object -Skip 1 | ForEach-Object { $module = @{}; $c = 0 } { $c++; $module["id_$c"] = $_ } { $module } 
    $id = Read-Host "input module id"
    Write-Host "`n>$($module["id_$id"])<"
    ollama run $module["id_$id"]
}

function aiw {
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
        $dest_folder_path_old = "$HOME\core\prs\ofai\works\$dest_folder_name"
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

function it {
    & $HOME\core\prs\pwsh\init.ps1
    rs
}

function prg {
    pr; git status
}

function er {
    param(
        [string]$search
    )
    (Get-StartApps | Where-Object { $_.Name -match $search }) | 
    ForEach-Object -Begin { $runid = 0; $result = @() }-Process { $runid++; $result += [PSCustomObject]@{
            RunID = $runid
            Name  = $_.Name
            AppID = $_.AppID
        } }-End { $result | Format-Table -AutoSize -Wrap }
    if ($result) {
        $run = Read-Host 'input run id (Enter as 1)'
        if ($run) { $run = $run }else { $run = 1 }
        $result | Where-Object { $_.RunID -eq $run } |
        ForEach-Object { if ($_.AppID -match '[a-zA-Z]:') { explorer.exe $_.AppID }else { explorer.exe "shell:appsfolder\$($_.AppID)" } }
    }
    else { Write-Host 'not find with startapps' }
}
