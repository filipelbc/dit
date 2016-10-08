#!/usr/bin/env bash

./ditcmd list --all

./ditcmd -d "ditdir" list --all

./step tar -xf test_ditdir.tgz

./step mv .dit ../

./ditcmd list --all

./ditcmd -d "ditdir" list --all

./step rm -rf ../.dit ditdir
