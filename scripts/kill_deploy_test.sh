#!/usr/bin/env bash

for KILLPID in `ps ax | grep 'python -m tests.deploy' | awk ' { print $1;}'`; do
  kill $KILLPID;
done
