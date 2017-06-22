#!/usr/bin/bash
for arg in "$@"
do
 python3 testcall.py $arg
done
