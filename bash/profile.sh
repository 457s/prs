#! /bin/bash

# 提示符
PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '

# PATH
if [[ "$PATH" != *"$HOME/core/prs/bin"* ]]; then
    PATH="$HOME/core/prs/bin:$PATH"
fi

