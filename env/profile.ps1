# 个人配置
Import-Module ROOT\wq.psm1 -DisableNameChecking -Force
if ($env:path -notmatch '\\prs\\') { $env:path += ";ROOT\bin" }
