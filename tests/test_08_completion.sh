#!/usr/bin/env bash

source ../bash-completion/dit

step(){
    echo '---------------------------------------------------'
    echo "$ $2<TAB><TAB>"

    COMP_LINE="$2"
    COMP_WORDS=( $COMP_LINE )
    COMP_CWORD=$1
    _dit
    echo ${COMPREPLY[*]} | tr ' ' '\n' | sort | tr '\n' ' '
    echo ''
}

step 1 "dit "
step 1 "dit -"
step 2 "dit -d "
step 3 "dit -d ditdir "
step 3 "dit -d ditdir e"
step 4 "dit -d ditdir o -"
step 4 "dit -d ditdir w "
step 4 "dit -d ditdir w g"
step 4 "dit -d ditdir w ."
step 4 "dit -d ditdir w ./"
step 4 "dit -d ditdir w ././"
step 4 "dit -d ditdir w ././t"
