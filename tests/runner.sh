#!/usr/bin/env bash

for i in test_*.sh; do
    echo -ne "$i    "
    out=${i%.*}.out
    ok=${i%.*}.ok
    diff=${i%.*}.diff
    ./$i > $out 2>&1
    diff $out $ok > $diff
    if [ -s $diff ]; then
        echo "fail"
        break
    else
        echo "pass"
    fi
done
