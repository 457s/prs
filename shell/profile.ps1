# 终端装饰
Invoke-Expression (starship init powershell)
$PSVersionTable | Out-String -Stream | Select-Object -First 5

# 个人配置
Import-Module ROOT\shell\wq.psm1 -DisableNameChecking -Force
if ($env:path -notmatch '\\prs\\shell\\') { $env:path += ";ROOT\shell\bin" }
