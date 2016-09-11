#!/usr/bin/env bash

./ditcmd workon 't1'
./ditcmd halt

./ditcmd workon 't1'
./ditcmd halt
./ditcmd halt
./ditcmd halt 't1'

./ditcmd workon 't10'
./ditcmd halt

./ditcmd workon 't10'
./ditcmd conclude

./ditcmd workon 't7'
./ditcmd workon 't7'
