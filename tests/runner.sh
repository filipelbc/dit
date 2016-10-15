#!/usr/bin/env bash

for i in $@
do
    echo -ne "$i    "
    out=${i%.*}.out
    ok=${i%.*}.ok
    diff=${i%.*}.diff
    ./$i &> $out
    diff -u $ok $out > $diff
    if [ -s $diff ]; then
        echo "fail"
        cat $diff
        exit 1
    else
        echo "pass"
    fi
done
