#! /bin/bash

. $HOME/wq/prs/lib/bash/wq.sh

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
