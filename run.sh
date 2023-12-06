#!/bin/bash

# Function to create and activate virtual environment
create_and_activate_venv() {
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
}

# Function to execute Python scripts
execute_python_scripts() {
    echo "Ingesting Site Information..."
    python ./python/ingestor/site_ingestor.py

    echo "Ingesting Climate information..."
    python ./python/ingestor/climDataIngestor.py

    echo "Fitting ML Models..."
    python ./python/analysis/analysis.py
}

# Check if any flags were provided
FLAG_PROVIDED=false

# Parse flags
while getopts ":I" option; do
    case $option in
        I)
            FLAG_PROVIDED=true
            create_and_activate_venv
            execute_python_scripts
            echo "Running Django server"
            python3 ./python/django_proj/manage.py runserver
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
    esac
done

# If no flags were provided, just run the Django server
if [ "$FLAG_PROVIDED" = false ]; then
    echo "No flags provided, running Django server..."
    python3 ./python/django_proj/manage.py runserver
fi
