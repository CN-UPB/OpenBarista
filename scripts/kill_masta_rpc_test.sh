#!/usr/bin/env bash

for KILLPID in `ps ax | grep 'python -m tests.rpc_client_test' | awk ' { print $1;}'`; do
  kill $KILLPID;
done
