#!/bin/sh

# these data should be parameters

RELATION=$0
PORT=$1
IFACE=$2
IP=$3
EXTERNAL=$4

# start python code

echo "Creating interface"

FILE=/etc/network/interfaces

python /tmp/decaf-vnf-manager/add_iface.py $RELATION $PORT $IFACE $IP $EXTERNAL $FILE

# startup interface

ifup $IFACE

echo Interface successfully created or not ?
