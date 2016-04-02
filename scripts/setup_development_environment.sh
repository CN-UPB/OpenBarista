#!/usr/bin/env bash

CURRENT_DIR=$(pwd)

cd "$(dirname "$0")/.."


if ! sudo /bin/which rabbitmqctl >/dev/null 2>&1; then
	echo "RabbitMQ is not installed."
	read -p "Do you wish to install RabbitMQ? (Y/n)" -n 1 -r
	echo    # (optional) move to a new line
	if [[ $REPLY =~ ^[Yy]$ ]] || [ -z $REPLY ]
	then
		echo "Please provide root privileges to install."
		echo "\$ sudo apt-get -y install rabbitmq-server"
		sudo apt-get -y install rabbitmq-server
	fi
fi

echo "#################################"
echo ""
echo "Installing virtual environment..."
echo ""
echo "#################################"
sudo apt-get install python-virtualenv
virtualenv -p $(which python) .env


echo "#################################"
echo ""
echo "Virtual environment was installed to '.env'"
echo ""
echo "#################################"

if [ -f ".env/bin/activate" ]; then
    source ".env/bin/activate"


    echo "#################################"
    echo ""
    echo "Upgrade pip"
    echo ""
    echo "#################################"
    pip install --upgrade pip


    echo "#################################"
    echo ""
    echo "Installing tools"
    echo ""
    echo "#################################"
    pip install pip-tools
    pip install Sphinx


    echo "#################################"
    echo ""
    echo "install postgresql"
    echo ""
    echo "#################################"
    sudo apt-get install postgresql postgresql-contrib python-dev postgresql-server-dev-all


    echo "#################################"
    echo ""
    echo "build postgresql driver psycopg2"
    echo ""
    echo "#################################"
    pip install psycopg2


    echo "#################################"
    echo ""
    echo "create postgresql db decaf_storage"
    echo ""
    echo "#################################"
    cat <<EOC | exec sudo -i -u postgres /bin/sh -
cat <<EOF | psql
CREATE USER pgdecaf WITH PASSWORD 'pgdecafpw';
DROP DATABASE decaf_storage;
CREATE DATABASE decaf_storage OWNER pgdecaf;
\c decaf_storage
CREATE EXTENSION "uuid-ossp";
EOF

EOC


    echo "#################################"
    echo ""
    echo "Finished installing tools"
    echo ""
    echo "#################################"
    echo ""
    echo "Activate virtualenvironment with"
    echo "source .env/bin/activate"
else
    echo "ERROR: Could not source virtual environment"
fi

cd $CURRENT_DIR


