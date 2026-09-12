# 提示符
function prompt {
    Write-Host "PS " -NoNewline -ForegroundColor Green
<<<<<<< HEAD
    Write-Host $executionContext.SessionState.Path.CurrentLocation -NoNewline -ForegroundColor Cyan
=======
    Write-Host $executionContext.SessionState.Path.CurrentLocation -NoNewline -ForegroundColor Blue
>>>>>>> f2ac163 (.)
    Write-Host "> " -NoNewline
    " "
}

# PATH
if ($env:path -notmatch '\\core\\prs\\bin') { $env:path += ";$HOME\core\prs\bin" }

