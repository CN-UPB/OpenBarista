#!/bin/bash

/etc/init.d/rabbitmq-server start
/etc/init.d/postgresql start

#some delay so postgres can start up
sleep 3
/home/openbarista/scripts/recreate_database.sh
/home/openbarista/scripts/create_dirs.sh
rm /var/run/decaf/*

/usr/local/bin/storaged start &

# some sleeping required as storaged seems to be the most important component
sleep 5
/usr/local/bin/deploymentd start
/usr/local/bin/placementd start
/usr/local/bin/oscard
/usr/local/bin/vnf_manager_adapterd start
/usr/local/bin/componentmanagerd start

/usr/local/bin/specificationd fg