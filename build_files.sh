#!/bin/bash

# Ensure we use python3.11 for the build
export PYTHON_VERSION=3.11

echo "Installing dependencies..."
python3.11 -m pip install -r requirements.txt

echo "Collecting static files..."
# Make sure the directory exists before collecting
mkdir -p staticfiles
python3.11 manage.py collectstatic --no-input

echo "Build complete!"
