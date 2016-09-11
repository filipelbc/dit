#!/usr/bin/env bash

./ditcmd new t1 -d 'test'

./ditcmd new g1/t2 -d 'test'

./ditcmd new g2/g3/t3 -d 'test'

./ditcmd new /t4 -d 'test'

./ditcmd new /g4/t5 -d 'test'

./ditcmd new g5//t6 -d 'test'

./ditcmd new //t7 -d 'test'

./ditcmd new g5/s4/t8 -d 'test'

./ditcmd new g5//t9 -d 'test'

./ditcmd new ././t7 -d 'fail, already exists'

./ditcmd new t10 -d 'test'

./step tree './ditdir'
