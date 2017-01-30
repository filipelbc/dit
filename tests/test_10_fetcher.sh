#!/usr/bin/env bash

fetcher_fn=.fetcher

setup_fetcher(){
    cat test_10_fetcher.script > ./ditdir/g5/$fetcher_fn
    chmod +x ./ditdir/g5/$fetcher_fn

    cat test_10_fetcher.script_bad > ./ditdir/g1/$fetcher_fn
    chmod +x ./ditdir/g1/$fetcher_fn

    echo '#!/usr/bin/env bash' > ./ditdir/g4/$fetcher_fn
    chmod +x ./ditdir/g4/$fetcher_fn
}

echo '---------------------------------------------------'
echo "$ setup_fetcher"
setup_fetcher

./ditcmd new --fetch g5/g6/t11
./ditcmd list --verbose g5/g6/t11

./ditcmd new --fetch ././t12 # no fetcher found
./ditcmd list --verbose ././t12  # no task found

./ditcmd new --fetch g4/./t13  # no data fetched
./ditcmd list --verbose g4/./t13  # no task found

./ditcmd switchto --new g5/g6/t14 -: "This task will be moved a lot!"
./ditcmd set -: ISSUE NUMBER
./ditcmd set -: From Elsewhere
./ditcmd note -: 'Wololo!'
./ditcmd halt
./ditcmd list --verbose g5/g6

./ditcmd move --fetch g5/g6/t14 g5/g6/t15
./ditcmd list --verbose g5/g6
./ditcmd workon g5/g6/t15
./ditcmd move g5/g6/t15 g5/g7/t16
./ditcmd status
./ditcmd halt

./ditcmd fetch g1//t2

./ditcmd list --all
./ditcmd status
