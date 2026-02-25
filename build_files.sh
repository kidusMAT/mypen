#!/bin/bash

echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

echo "Collecting static files..."
# Make sure the directory exists before collecting
mkdir -p staticfiles
python3 manage.py collectstatic --no-input

echo "Build complete!"
