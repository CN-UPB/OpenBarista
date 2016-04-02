#!/usr/bin/env bash

sudo kill -9 `cat /var/run/decaf/vnf_manager_adapterd.pid`
sudo rm -rf /var/run/decaf/vnf_manager_adapterd.pid
