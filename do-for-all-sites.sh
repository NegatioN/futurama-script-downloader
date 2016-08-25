#!/usr/bin/env bash

for word in "$@"
do
{
    python3 remade_script_parser.py $word
    } || { # catch
    # save log for exception
    echo "fail $word"
}
done
