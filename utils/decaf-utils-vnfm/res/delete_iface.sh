#!/bin/sh

# these data should be parameters

# start python code

FILE=/etc/network/interfaces
python delete_iface.py $IFACE $FILE

# stop interface

ifdown $IFACE
