#!/usr/bin/env bash

./ditcmd list
./ditcmd list --id-only

./ditcmd list --all
./ditcmd list --all --id-only

./ditcmd list --concluded
./ditcmd list --concluded --id-only

./ditcmd list PREVIOUS
./ditcmd list --id-only PREVIOUS

./ditcmd list CURRENT
./ditcmd list --id-only CURRENT

./ditcmd status --verbose

./ditcmd status --id-only
