#!/bin/bash
set -e

echo 'Setting up databases...'
# The postgres server is started automatically by the postgres container

# Wait for the server to be ready
sleep 10

echo 'Creating databases...'
psql -U postgres -c 'CREATE DATABASE loyalty_db;'
psql -U postgres -c 'CREATE DATABASE menu_db;'
psql -U postgres -c 'CREATE DATABASE pos_db;'

echo 'Database setup complete!'
