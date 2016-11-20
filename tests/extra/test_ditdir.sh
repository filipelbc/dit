#!/usr/bin/env bash

./ditcmd list --all -v

./ditcmd -d "ditdir" list --all -v

./step tar -xzf test_ditdir.tar.gz

./step mv .dit ../

./ditcmd list --all -v

./ditcmd -d "ditdir" list --all -v

./step rm -rf ../.dit ditdir
