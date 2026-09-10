#! /bin/bash

if [[ "$PATH" != *"$HOME/core/prs/bin"* ]]; then
    PATH="$HOME/core/prs/bin:$PATH"
fi

if [[ "$PATH" != *"$HOME/bin"* ]]; then
    PATH="$HOME/bin:$PATH"
fi
