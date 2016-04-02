#!/usr/bin/env bash

for KILLPID in `ps ax | grep 'mastad' | awk ' { print $1;}'`; do
  kill -9 $KILLPID;
done
