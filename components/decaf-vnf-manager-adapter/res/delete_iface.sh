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

INTERFACE_ID=$1
PHYSICAL_IFACE=$2

# stop interface

ifdown $PHYSICAL_IFACE

# start python code

FILE=/etc/network/interfaces
python /tmp/decaf-vnf-manager/delete_iface.py $INTERFACE_ID $FILE