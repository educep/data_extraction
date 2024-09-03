#!/bin/bash

# Create a Python virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Update pip
python -m pip install --upgrade pip

# Install requirements from a file
pip install -r requirements.txt

echo "Virtual environment has been set up."
