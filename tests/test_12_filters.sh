#!/usr/bin/env bash

./ditcmd halt

./ditcmd set --task 'g5/g7/t16' 'pName' 'pvalue'

./ditcmd list --all --concluded --verbose --from '19h21min' --to '20h'
./ditcmd list --all --concluded --verbose --where 'pName' 'p(v|V)alue' --sum
./ditcmd list --all --concluded --verbose --where 'pName' 'p(v|V)alue' --from '19h21min' --to '20h'

./ditcmd list --verbose --from '18h' ././t10
./ditcmd list --verbose --from '19h21min' ././t10
./ditcmd list --verbose --from '21h' ././t10
./ditcmd list --verbose --to '21h' ././t10
./ditcmd list --verbose --to '20h' ././t10
./ditcmd list --verbose --to '18h' ././t10

./ditcmd list --verbose --from '19h36min' --to '20h31min' -c ././t10

./ditcmd list --verbose --from '18h' g1//t2
./ditcmd list --verbose --to '20h' g1//t2

./ditcmd list --verbose --from '2016-09-10-19:00' --to '2016-09-10-20:00' ././t10

./ditcmd list --verbose --from '19:00' --to '20:00' ././t10
