#!/usr/bin/env bash

set -o errexit  # exit on error
pip install --upgrade pip
pip install -r requirements.txt
python seed_database.py  # Run seed script
flask db upgrade  # Run any migrations
mkdir -p staticfiles
cp -r app/static/* staticfiles/