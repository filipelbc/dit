#!/usr/bin/env bash

run_tests() {
    for i in "$@"; do
        echo -ne "$i    "
        out=${i%.*}.out
        ok=${i%.*}.ok
        diff=${i%.*}.diff
        ./$i > $out 2>&1
        diff $out $ok > $diff
        if [ -s $diff ]; then
            echo "fail"
            exit 1
        else
            echo "pass"
        fi
    done
}

run_tests $(ls test_*.sh)
