#!/usr/bin/env bash

set -o errexit  # Exit on error

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Remove old migrations (optional)
rm -rf migrations/

# Initialize and generate fresh migrations
flask db init
flask db migrate -m "Recreate migrations"
flask db upgrade  # Apply migrations

# Seed the database AFTER migrations
python seed_database.py  

# Handle static files
mkdir -p staticfiles
cp -r app/static/* staticfiles/
