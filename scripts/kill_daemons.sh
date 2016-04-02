#!/usr/bin/env bash

kill `cat /var/run/decaf/masta.pid`
kill `cat /var/run/decaf/oscard.pid`
kill `cat /var/run/decaf/deploymentd.pid`
kill `cat /var/run/decaf/storaged.pid`
kill `cat /var/run/decaf/componentmanagerd.pid`

ps aux | grep specificationd | awk '{print $2}' | xargs kill -9
ps aux | grep storaged | awk '{print $2}' | xargs kill -9

rm /var/run/decaf/specificationd.pid
rm /var/run/decaf/storaged.pid
rm /var/run/decaf/componentmanagerd.pid
rm /var/run/decaf/deploymentd.pid
rm /var/run/decaf/oscard.pid
rm /var/run/decaf/mastad.pid
