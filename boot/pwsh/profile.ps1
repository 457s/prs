# 个人配置
Import-Module ROOT\lib\pwsh\core.psm1 -DisableNameChecking -Force
if ($env:path -notmatch '\\prs\\bin') { $env:path += ";ROOT\bin" }
