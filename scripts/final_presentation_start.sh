#!/usr/bin/env bash

storaged start;
sleep 10;
mastad start;
vnf_manager_adapterd start;
deploymentd start;
example_scalingd start;
placementd start;