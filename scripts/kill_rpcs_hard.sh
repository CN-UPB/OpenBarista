#!/usr/bin/env bash

for KILLPID in `ps ax | grep 'python -m' | awk ' { print $1;}'`; do
  kill -9 $KILLPID;
done

sudo rabbitmqctl stop_app
sudo rabbitmqctl force_reset
sudo rabbitmqctl start_app
