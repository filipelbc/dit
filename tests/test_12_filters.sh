#!/usr/bin/env bash

./ditcmd halt

./ditcmd set 'g5/g7/t16' -: 'pName' 'pvalue'

./ditcmd list --all --concluded --verbose --from '19h 20min' --to '20h'

./ditcmd list --all --concluded --verbose --where 'pName' 'p(v|V)alue' --sum

./ditcmd list --all --concluded --verbose --where 'pName' 'p(v|V)alue' --from '19h 20min' --to '20h'
