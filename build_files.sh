#!/bin/bash

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
# Ensure staticfiles directory exists
mkdir -p staticfiles
python3 manage.py collectstatic --no-input

echo "Build complete!"
