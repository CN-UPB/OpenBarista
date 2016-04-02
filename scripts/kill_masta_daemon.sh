#!/usr/bin/env bash

kill `cat /var/run/decaf/mastad.pid`
rm /var/log/decaf/mastad.log