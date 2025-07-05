#!/bin/bash

# VCV Rack Module Search Build Script
# This script builds the complete module search system

set -e  # Exit on any error

# Configuration
REPO_URL="https://github.com/VCVRack/library.git"
TARGET_DIR="library"
SITE_DIR="site"
CACHE_DIR="cache"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to clone or update VCV library repository
clone_or_update_library() {
    log_info "Processing VCV Rack library repository..."
    
    if [ -d "$TARGET_DIR" ]; then
        log_info "Directory '$TARGET_DIR' already exists. Pulling latest changes..."
        cd "$TARGET_DIR"
        if git pull origin; then
            log_info "Repository updated successfully"
        else
            log_error "Failed to update repository"
            exit 1
        fi
        cd ..
    else
        log_info "Cloning repository into '$TARGET_DIR'..."
        if git clone "$REPO_URL" "$TARGET_DIR"; then
            log_info "Repository cloned successfully"
        else
            log_error "Failed to clone repository"
            exit 1
        fi
    fi
}

# Function to run data processing
run_data_processing() {
    log_info "Running data processing (parsing manifests and downloading images)..."
    if python3 process_data.py; then
        log_info "Data processing completed successfully"
    else
        log_error "Data processing failed"
        exit 1
    fi
}

# Function to generate search file
generate_search_file() {
    log_info "Generating search file..."
    if python3 generate_search_file.py; then
        log_info "Search file generated successfully"
    else
        log_error "Search file generation failed"
        exit 1
    fi
}

# Function to deploy files to site directory
deploy_files() {
    log_info "Deploying files to site directory..."
    
    # Create site directory structure
    mkdir -p "$SITE_DIR/images"
    
    # Copy main files
    if cp index.html "$SITE_DIR/"; then
        log_info "Copied index.html to site/"
    else
        log_error "Failed to copy index.html"
        exit 1
    fi
    
    if cp search_file.json "$SITE_DIR/"; then
        log_info "Copied search_file.json to site/"
    else
        log_error "Failed to copy search_file.json"
        exit 1
    fi
    
    # Copy cache images to site
    if [ -d "$CACHE_DIR" ]; then
        if cp -r "$CACHE_DIR/." "$SITE_DIR/images/"; then
            log_info "Copied cached images to site/images/"
        else
            log_error "Failed to copy cached images"
            exit 1
        fi
    else
        log_warn "Cache directory not found, skipping image copy"
    fi
}

# Main build function
main() {
    log_info "Starting VCV Rack Module Search build process..."
    
    clone_or_update_library
    run_data_processing
    generate_search_file
    deploy_files
    
    log_info "Build process completed successfully!"
    log_info "Site files are ready in the '$SITE_DIR' directory"
}

# Run main function
main "$@"