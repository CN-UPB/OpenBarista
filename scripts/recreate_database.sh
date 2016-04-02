#!/usr/bin/env bash


cat <<EOC | exec sudo -i -u postgres /bin/sh -
cat <<EOF | psql
CREATE USER pgdecaf WITH PASSWORD 'pgdecafpw';
DROP DATABASE decaf_storage;
CREATE DATABASE decaf_storage OWNER pgdecaf;
\c decaf_storage
CREATE EXTENSION "uuid-ossp";
EOF

EOC