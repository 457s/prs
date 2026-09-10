#! /bin/bash

. $HOME/core/prs/bash/lib/core.sh

main(){
    subcommand=$1
    shift
    if type $subcommand >/dev/null 2>&1;then
        $subcommand $@
    else
        echo "the command of $subcommand is not exists"
    fi
}
main $@
