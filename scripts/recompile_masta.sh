#!/usr/bin/env bash

kill `cat /var/run/decaf/mastad.pid`
rm /var/run/decaf/mastad.pid
rm /var/log/decaf/mastad.log
cd ~/decaf/components/decaf-masta/
make install