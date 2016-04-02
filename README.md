# File structure

The file structure looks as follows:

### Components

```/components/\<componentpackagename\>/\<packagefiles\>```

An example component skeleton can be found in ```/components/template.```

### Utility-Methods
they can be used by more than one Component

```/utils/\<utilpackagename\>/\<packagefiles\>```


# Getting started

The development environment can be set up with the following steps:

## Prerequisites
tested on ubuntu 14.04
and debian 8
with python 2.7

## clone repository

```bash
git clone irb-git@git.cs.upb.de:pg-decaf/Prototype.git
cd Prototype
./decaf_utils.sh
# select *Environment*
# then select *All*
```


You will be asked for root privileges.
The routine will
- install all nessesary debian packages
- set up a python environment
- install needed python packages
- build all components
- create needed directories
- copy default configs into ```/etc/decaf/```

Logs of components can be found in ```/var/log/decaf/```

Under components you can manage all your components


# Getting started Manually
You can also set up the environment manually with the following steps.

## Prerequisites

Before getting started we need the following prerequisites:
- Install RabbitMQ
- Set up python virtualenv

### Install RabbitMQ

Debian:

Add the following line to */etc/apt/sources.list*

```apt_sources
deb http://www.rabbitmq.com/debian/ testing main
```
and execute these commands
```bash
wget https://www.rabbitmq.com/rabbitmq-signing-key-public.asc
sudo apt-key add rabbitmq-signing-key-public.asc
sudo apt-get update && sudo apt-get install rabbitmq-server
```


### Set up python virtualenv

Now we have to set up the the virtual environment.
```bash
virtualenv -p <python_binary> <virtualenv_name>
```
Finally we have to activate the environment.
```bash
source <virtualenv_path>/bin/activate
```

## Install components

To install the components using make execute
```bash
make install
```

## Start a new component

If you want to create a new component, have a look into the example-scaling component.
