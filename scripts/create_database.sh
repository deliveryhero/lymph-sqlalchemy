#!/bin/bash

PSQL=${PSQL:-"psql"}

DBNAME="${DBNAME:-"lymph-test-sqlalchemy"}"

echo "Creating database ${DBNAME}"
${PSQL} <<EOF
  CREATE DATABASE "${DBNAME}";
  \c "${DBNAME}"
  CREATE EXTENSION postgis;
EOF
