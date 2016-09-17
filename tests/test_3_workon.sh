#!/usr/bin/env bash

./ditcmd workon 't1'
./ditcmd halt

./ditcmd workon 't1'
./ditcmd halt
./ditcmd halt
./ditcmd halt 't1'

./ditcmd workon 't10'
./ditcmd halt
./ditcmd status

./ditcmd workon 't10'
./ditcmd conclude
./ditcmd status

./ditcmd workon 't7'
./ditcmd workon 't7'
./ditcmd status

./ditcmd switchto 'g5/t6'
./ditcmd status
./ditcmd halt
./ditcmd status

./ditcmd workon 't10'   # no such task
./ditcmd workon '/t10'  # no such task

./ditcmd workon '//t10'
./ditcmd status
