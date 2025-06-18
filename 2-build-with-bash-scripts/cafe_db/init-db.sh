#!/bin/bash
set -e

echo 'Setting up databases...'
# Wait for PostgreSQL to start
sleep 5

echo 'Creating databases...'
psql -U postgres -c 'CREATE DATABASE loyalty_db;'
psql -U postgres -c 'CREATE DATABASE menu_db;'
psql -U postgres -c 'CREATE DATABASE pos_db;'

echo 'Databases created successfully!'
