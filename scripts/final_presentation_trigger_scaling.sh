#!/usr/bin/env bash

ALARM_ID=$1
VALUE=$2

python ./components/decaf-masta/tests/trigger_alarm.py $ALARM_ID $VALUE