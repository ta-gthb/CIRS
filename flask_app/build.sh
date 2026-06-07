#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Compile translations
python -m babel.messages.frontend compile -d app/translations

# Initialize/Update Database
python setup_db.py
