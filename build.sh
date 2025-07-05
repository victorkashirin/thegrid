#!/bin/bash

# Script to clone VCVRack library repository

REPO_URL="https://github.com/VCVRack/library.git"
TARGET_DIR="library"

echo "Cloning VCVRack library repository..."

# Check if the directory already exists
if [ -d "$TARGET_DIR" ]; then
    echo "Directory '$TARGET_DIR' already exists."
    echo "Pulling latest changes..."
    cd "$TARGET_DIR"
    git pull origin 
    cd ..
else
    echo "Cloning repository into '$TARGET_DIR'..."
    git clone "$REPO_URL" "$TARGET_DIR"
fi

# Check if the operation was successful
if [ $? -eq 0 ]; then
    echo "Repository successfully cloned/updated in '$TARGET_DIR'"
else
    echo "Error: Failed to clone/update repository"
    exit 1
fi

echo "Parsing search and downloading images..."
python3 download_images.py

echo "Generating search file..."
python3 generate_search_file.py

echo "Done!"


mkdir -p site/images
cp index.html site/
mv search_file.json site/
cp -r cache/ site/images/