#!/usr/bin/env bash

./ditcmd list --all -v

./ditcmd -d "ditdir" list --all -v

./step tar -xf test_ditdir.tgz

./step mv .dit ../

./ditcmd list --all -v

./ditcmd -d "ditdir" list --all -v

./step rm -rf ../.dit ditdir
