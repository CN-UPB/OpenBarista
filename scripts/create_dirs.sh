#!/usr/bin/env bash

CFGDIR="/etc/decaf"
RUNDIR="/var/run/decaf"
LOGDIR="/var/log/decaf"
TMPDIR="/tmp/decaf"


if [ ! -d $CFGDIR ]; then
    sudo mkdir -p $CFGDIR
    sudo chown -R $USER:$USER $CFGDIR
fi
if [ ! -d $RUNDIR ]; then
    sudo mkdir -p $RUNDIR
    sudo chown -R $USER:$USER $RUNDIR
fi
if [ ! -d $LOGDIR ]; then
    sudo mkdir -p $LOGDIR
    sudo chown -R $USER:$USER $LOGDIR
fi
if [ ! -d $TMPDIR ]; then
    sudo mkdir -p $TMPDIR
    sudo chown -R $USER:$USER $TMPDIR
fi
