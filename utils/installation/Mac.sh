#!/bin/bash

set -e  # stop on error

REPO_URL="https://github.com/COSC-499-W2025/capstone-project-team-10.git"
REPO_DIR="capstone-project-team-10"

# --- Clone repo if missing ---
if [ ! -d "$REPO_DIR" ]; then
    echo "Cloning repository..."
    git clone "$REPO_URL"
fi

cd "$REPO_DIR"

# --- Create venv if missing ---
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# --- Activate venv ---
source venv/bin/activate

# --- Install dependencies if missing ---
if ! pip show nltk > /dev/null 2>&1; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "Dependencies already installed. Skipping..."
fi

# --- Setup NLTK data ---
if [ ! -d "$HOME/nltk_data" ]; then
    echo "Setting up NLTK data..."
    python utils/setup_nltk_data.py
else
    echo "NLTK data already exists. Skipping..."
fi

# --- Run app ---
echo "Running application..."
python -m src.main