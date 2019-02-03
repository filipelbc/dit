#!/usr/bin/env bash

./ditcmd note 'This is a simple note.'

./ditcmd note --task t1 'This is another simple note.'

./ditcmd note --task t1 ''

./ditcmd note --task g5/t6 'Note, note, note! This one is a very long note.'

./ditcmd set pName pValue

./ditcmd set --task t1 "Some Name" "Some Value"

./ditcmd set --task t1 '' ''

./ditcmd set --task g5/t6 s_name s_value

./ditcmd list --concluded .

./ditcmd list g5//t6
