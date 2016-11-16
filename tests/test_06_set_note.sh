#!/usr/bin/env bash

./ditcmd note -: 'This is a simple note.'

./ditcmd note t1 -: 'This is another simple note.'

./ditcmd note t1 -: ''

./ditcmd note g5/t6 -: 'Note, note, note! This one is a very long note.'

./ditcmd set -: pName pValue

./ditcmd set t1 -: "Some Name" "Some Value"

./ditcmd set t1 -: '' ''

./ditcmd set g5/t6 -: s_name s_value

./ditcmd list --concluded .

./ditcmd list g5//t6
