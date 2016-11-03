#!/usr/bin/env bash

./ditcmd workon 't1'
./ditcmd halt

./ditcmd workon '0'
./ditcmd halt

./ditcmd workon '0'
./ditcmd halt
./ditcmd halt
./ditcmd halt 't1'

./ditcmd workon '0'
./ditcmd cancel
./ditcmd status

./ditcmd workon 't1'
./ditcmd cancel 't10'
./ditcmd workon 't10'
./ditcmd cancel 't1'
./ditcmd cancel
./ditcmd list

./ditcmd workon 't10'
./ditcmd halt
./ditcmd workon '1'
./ditcmd halt
./ditcmd workon 'CURRENT'
./ditcmd halt
./ditcmd workon 'PREVIOUS'
./ditcmd halt
./ditcmd status

./ditcmd workon 't10'
./ditcmd conclude
./ditcmd status

./ditcmd workon 't7'
./ditcmd workon 't7'
./ditcmd status

./ditcmd workon '0/0/0'    # same as //t1
./ditcmd status

./ditcmd switchto 'g4/t5'
./ditcmd switchto '4/0/0'  # same as g5/./t6
./ditcmd switchto '1/0'    # same as g5/g6/t8
./ditcmd status
./ditcmd halt
./ditcmd status

./ditcmd workon 't10'   # no such task
./ditcmd workon '/t10'  # no such task
./ditcmd workon '2'     # no such task

./ditcmd workon '//t10'
./ditcmd status
