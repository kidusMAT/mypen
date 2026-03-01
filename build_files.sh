#!/bin/bash

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
# Ensure staticfiles directory exists
mkdir -p staticfiles
python manage.py collectstatic --no-input

echo "Build complete!"
