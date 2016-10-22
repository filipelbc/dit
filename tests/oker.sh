#!/usr/bin/env bash

for i in $@
do
    echo -ne "$i    "
    ok=${i%.*}.ok
    ./$i &> $ok
    echo "done"
done
