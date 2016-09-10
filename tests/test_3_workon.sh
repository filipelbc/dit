#!/usr/bin/env bash

./ditcmd workon 't1'
./ditcmd halt

./ditcmd workon 't1'
./ditcmd halt

./ditcmd workon 't2'
./ditcmd halt

./ditcmd workon 't2'
./ditcmd conclude

./ditcmd workon 't7'
