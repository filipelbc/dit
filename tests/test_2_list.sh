#!/usr/bin/env bash

./ditcmd list           # no current and nothing selected: same as "--all"

./ditcmd list --all     # everything

./ditcmd list '.'       # same as './.'

./ditcmd list 'g5'      # all subgroups of group g5

./ditcmd list 'g5/.'

./ditcmd list '/g5'     # same as 'g5'

./ditcmd list 'g5/g6'

./ditcmd list 'g5/g6/t8'

./ditcmd list 'g5/./t6'

./ditcmd list '/g5/t6'  # same as 'g5/./t6'

./ditcmd list '/g2'     # same as 'g2'

./ditcmd list 'g2/'     # same as 'g2/.'

./ditcmd list 't10'     # nothing to do, no such group

./ditcmd list '/t10'    # same as 't10'

./ditcmd list '//t10'   # same as ././t10

./ditcmd list 'g1//t2'
