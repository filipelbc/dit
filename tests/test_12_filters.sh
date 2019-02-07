#!/usr/bin/env bash

./ditcmd halt

./ditcmd set --task 'g5/g7/t16' 'pName' 'pvalue'

./ditcmd list --all --concluded --verbose --from '19:21' --to '20:00'
./ditcmd list --all --concluded --verbose --where 'pName' 'p(v|V)alue' --sum
./ditcmd list --all --concluded --verbose --where 'pName' 'p(v|V)alue' --from '19:21' --to '20:00'

./ditcmd list --verbose --from '18:00' ././t10
./ditcmd list --verbose --from '19:21' ././t10
./ditcmd list --verbose --from '21:00' ././t10
./ditcmd list --verbose --to '21:00' ././t10
./ditcmd list --verbose --to '20:00' ././t10
./ditcmd list --verbose --to '18:00' ././t10

./ditcmd list --verbose --from '19:36' --to '20:31' -c ././t10

./ditcmd list --verbose --from '18:00' g1//t2
./ditcmd list --verbose --to '20:00' g1//t2

./ditcmd list --verbose --from '2016-09-10-19:00' --to '2016-09-10-20:00' ././t10

./ditcmd list --verbose --from '0d-1h-10min' --to '-10min' ././t10
