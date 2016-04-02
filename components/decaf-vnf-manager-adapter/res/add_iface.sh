#!/bin/sh

##
# Copyright 2016 DECaF Project Group, University of Paderborn
# This file is part of the decaf orchestration framework
# All Rights Reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
##

# these data should be parameters

INTERFACE_ID=$1               # the type of the interface (in the specification)
TYPE=$2               # the type of the interface (in the specification)
INTERNAL=$3           # the name of the internal interface (in the specification)
EXTERNAL=$4           # the name of the external interface (in the specification)
IFACE=$5              # the physical name of the interface
INTERNAL_OR_PUBLIC=$6 # either "internal" or "public", stating which kind of interface

# start python code

echo "Creating interface"

FILE=/etc/network/interfaces

python /tmp/decaf-vnf-manager/add_iface.py $INTERFACE_ID $TYPE $INTERNAL $EXTERNAL $IFACE $INTERNAL_OR_PUBLIC $FILE

# startup interface

ifup $IFACE

echo Interface successfully created or not ?
