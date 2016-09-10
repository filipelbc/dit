#!/usr/bin/env bash

./ditcmd new t1 -d 'test'

./ditcmd new s1/t2 -d 'test'

./ditcmd new g1/s2/t3 -d 'test'

./ditcmd new /t4 -d 'test'

./ditcmd new /s3/t5 -d 'test'

./ditcmd new g2//t6 -d 'test'

./ditcmd new //t7 -d 'test'

./ditcmd new g2/s4/t8 -d 'test'

./ditcmd new g2//t7 -d 'test'

./ditcmd new //t7 -d 'fail, already exists'

./ditcmd new t2 -d 'test'

./step tree './ditdir'
