#!/bin/bash

/etc/init.d/rabbitmq-server start
/etc/init.d/postgresql start

/home/openbarista/scripts/recreate_database.sh
/home/openbarista/scripts/create_dirs.sh

/usr/local/bin/storaged start &
/usr/local/bin/deploymentd start &
/usr/local/bin/componentmanagerd &
/usr/local/bin/placementd start&
/usr/local/bin/oscard &
/usr/local/bin/specificationd start&
/usr/local/bin/vnf_manager_adapterd start

/usr/local/bin/componentmanagerd