#! /bin/bash

cat $HOME/core/prs/bash/profile.sh > $HOME/.profile
mkdir -p $HOME/bin && ln -sf $HOME/core/prs/bin/bas.sh $HOME/bin/bas

echo -e "\033[32mbash init done\033[0m"
