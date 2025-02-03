#!/usr/bin/env bash

set -o errexit  # exit on error
pip install --upgrade pip
pip install -r requirements.txt

# Check if the database is already seeded
if [ "$(python -c 'from your_app import db; from your_app.models import User; print(User.query.count())')" -eq 0 ]; then
  python seed_database.py  # Run seed script if the database is empty
else
  echo "Database already seeded, skipping seed step."
fi

flask db upgrade  # Run any migrations
mkdir -p staticfiles
cp -r app/static/* staticfiles/
