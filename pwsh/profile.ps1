# 提示符
function prompt {
    Write-Host "PS " -NoNewline -ForegroundColor Green
    Write-Host $executionContext.SessionState.Path.CurrentLocation -NoNewline -ForegroundColor Blue
    Write-Host "> " -NoNewline
    " "
}

# PATH
if ($env:path -notmatch '\\core\\prs\\bin') { $env:path += ";$HOME\core\prs\bin" }
