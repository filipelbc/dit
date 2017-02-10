#!/usr/bin/env bash

./ditcmd status
./ditcmd status --limit 0
./ditcmd status --limit 3

./ditcmd conclude
./ditcmd conclude
./ditcmd conclude
./ditcmd resume
./ditcmd workon t10
./ditcmd conclude

./ditcmd workon g5/g6/t8
./ditcmd switchto t11
./ditcmd conclude
./ditcmd conclude
./ditcmd workon t8
./ditcmd halt
