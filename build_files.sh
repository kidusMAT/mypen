#!/bin/bash

echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

echo "Collecting static files..."
# Ensure staticfiles directory exists
mkdir -p staticfiles
DATABASE_URL=postgres://dummy:dummy@localhost:5432/dummy DEBUG=1 python3 manage.py collectstatic --no-input

echo "Build complete!"
