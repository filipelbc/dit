#!/usr/bin/env bash

./ditcmd new t1 -: 'Group . Subgroup . Task t1'
./ditcmd new g1/t2 -: 'Group g1 Subgroup . Task t2'
./ditcmd new g2/g3/t3 -: 'Group g2 Subgroup g3 Task t3'
./ditcmd new /t4 -: 'Group . Subgroup . Task t4'
./ditcmd new /g4/t5 -: 'Group g4 Subgroup . Task t5'
./ditcmd new g5//t6 -: 'Group g5 Subgroup . Task t6'
./ditcmd new //t7 -: 'Group . Subgroup . Task t7'
./ditcmd new g5/g6/t8 -: 'Group g5 Subgroup g6 Task t8'
./ditcmd new g5//t9 -: 'Group g5 Subgroup . Task t9'
./ditcmd new t10 -: 'Group . Subgroup . Task t10'

./ditcmd new ././t7 -: '. . t7, fails: already exists'
./ditcmd new _foo -: 'fails: invalid task name'
./ditcmd new .foo -: 'fails: invalid task name'
./ditcmd new _foo/bar -: 'fails: invalid group name'
./ditcmd new .foo/bar -: 'fails: invalid group name'

./list
