#!/usr/bin/env bash

./ditcmd workon --at -1d18h36min ././t10
./ditcmd halt --at -1d19h32min
./ditcmd conclude --at -1d20h11min
./ditcmd list -v ././t10
