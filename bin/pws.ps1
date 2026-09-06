. $HOME\core\prs\pwsh\lib\core.ps1

function main {
    param($subcommand)

    if(Get-Command -CommandType Function -Name $subcommand -ErrorAction SilentlyContinue)
        {& $subcommand @args}
    else
        {Write-Host "the command of $subcommand is not exists";exit 1}
}
main @args
