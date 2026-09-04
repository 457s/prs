#! /bin/bash

fc(){
    echo
    echo "$PATH"|tr ':' '\n'| while IFS= read -r row;do
        echo -e "\033[33m""$row""\033[0m"
        ls -la "$row" 2>/dev/null|awk -v name="$*" '
        $9~name{for(i=1;i<=NF;i++)
                {if(i==9)
                    {printf "\033[31m""%s""\033[0m",$i}
                else
                    {printf "%s",$i}
                if(i<NF){printf " "}
                }
            printf "\n"
            }'
        done
}

hl(){
    if [[ -z "$*" ]];then
        cat $HOME/wq/prs/lib/bash/core.sh|grep -oP '^.+(?=\(\){$)'|column -x
    else
        cat $HOME/wq/prs/lib/bash/core.sh|sed -n "/^$*(){/,/^}/p"
    fi
}