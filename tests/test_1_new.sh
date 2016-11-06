#!/usr/bin/env bash

./ditcmd new t1 -: '. . t1'
./ditcmd new g1/t2 -: 'g1 . t2'
./ditcmd new g2/g3/t3 -: 'g2 g3 t3'
./ditcmd new /t4 -: '. . t4'
./ditcmd new /g4/t5 -: 'g4 . t5'
./ditcmd new g5//t6 -: 'g5 . t6'
./ditcmd new //t7 -: '. . t7'
./ditcmd new g5/g6/t8 -: 'g5 g6 t8'
./ditcmd new g5//t9 -: 'g5 . t9'
./ditcmd new t10 -: '. . t10'

./ditcmd new ././t7 -: '. . t7, fails: already exists'
./ditcmd new _foo -: 'fails: invalid task name'
./ditcmd new .foo -: 'fails: invalid task name'
./ditcmd new _foo/bar -: 'fails: invalid group name'
./ditcmd new .foo/bar -: 'fails: invalid group name'

./list
