#!/bin/bash

# Define the virtual environment directory name
VENV_DIR="venv"

# Create a Python virtual environment
echo "Creating virtual environment in ./$VENV_DIR"
python3 -m venv $VENV_DIR

# Check if the virtual environment was created successfully
if [ ! -d "$VENV_DIR" ]; then
    echo "Failed to create virtual environment."
    exit 1
fi

# Activate the virtual environment
# echo "Activating virtual environment"
# source $VENV_DIR/bin/activate

# Check for requirements.txt file
if [ ! -f "requirements.txt" ]; then
    echo "requirements.txt not found."
    deactivate
    exit 1
fi

# Install packages from requirements.txt
echo "Installing packages from requirements.txt"
pip install -r requirements.txt

PWD=`pwd`
echo $PWD
activate () {
    . $PWD/venv/bin/activate
}

activate

echo "Setup complete. Virtual environment is ready to use."