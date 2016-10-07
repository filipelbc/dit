#!/usr/bin/env bash

./ditcmd note -: 'this is a note'

./ditcmd note t1 -: 'this is another note'

./ditcmd note t1 -: ''

./ditcmd note g5/t6 -: 'note note note'

./ditcmd set -: foo bar

./ditcmd set t1 -: abu din

./ditcmd set t1 -: '' ''

./ditcmd set g5/t6 -: jas min

./ditcmd list --concluded .

./ditcmd list g5//t6
