#!/usr/bin/env bash

for i in test_*.sh; do
    echo -ne "$i    "
    ok=${i%.*}.ok
    ./$i > $ok 2>&1
    echo "done"
done
