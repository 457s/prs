# 终端装饰
Invoke-Expression (starship init powershell)
$PSVersionTable | Out-String -Stream | Select-Object -First 5

# 个人配置
Import-Module ROOT\wq.psm1 -DisableNameChecking -Force
if ($env:path -notmatch '\\prs\\') { $env:path += ";ROOT\bin" }
