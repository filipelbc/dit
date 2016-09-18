#!/usr/bin/env bash

./ditcmd list           # no current and nothing selected: same as "--all"

./ditcmd list --all     # everything

./ditcmd list '0'       # same as './.'

./ditcmd list 'g5'      # all subgroups of group g5
./ditcmd list '/g5'     # same as g5
./ditcmd list '4'       # same as g5

./ditcmd list 'g5/.'    # subgroup '' of group g5
./ditcmd list '4/0'     # same as 'g5/.'

./ditcmd list 'g5/g6'
./ditcmd list '4/1'     # same as 'g5/g6'

./ditcmd list 'g5/g6/t8'
./ditcmd list '4/1/0'   # same as 'g5/g6/t8'

./ditcmd list 'g5/./t6'
./ditcmd list '/g5/t6'  # same as 'g5/./t6'
./ditcmd list '4/0/0'   # same as 'g5/./t6'

./ditcmd list '/g2'     # same as 'g2'
./ditcmd list '2'       # same as 'g2'

./ditcmd list 'g2/'     # same as 'g2/.'
./ditcmd list '2/0'     # same as 'g2/.'

./ditcmd list 't10'     # nothing to do, no such group
./ditcmd list '/t10'    # same as 't10'

./ditcmd list '5'       # invalid group

./ditcmd list '//t10'   # same as ././t10
./ditcmd list '0/0/3'   # same as ././t10

./ditcmd list 'g1//t2'  # same as 'g1/./t2'
./ditcmd list '1/0/0'   # same as 'g1/./t2'
