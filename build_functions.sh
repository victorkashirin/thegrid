#!/bin/bash

# Build functions for VCV Rack Module Search
# This file contains modular functions for the build process

# Source configuration
source "$(dirname "${BASH_SOURCE[0]}")/config.sh"

# Function to set up the build environment
setup_environment() {
    log_info "Setting up build environment..."

    # Create necessary directories
    if ! mkdir -p "$CACHE_DIR" "$SITE_DIR"; then
        log_error "Failed to create directories"
        return 1
    fi

    # Check Python dependencies
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        return 1
    fi

    # Check if required Python modules are available
    if ! python3 -c "import json, requests, PIL" &> /dev/null; then
        log_error "Required Python modules not available (json, requests, PIL)"
        return 1
    fi

    log_info "Build environment setup completed"
    return 0
}

# Function to clone or update VCV library repository
clone_or_update_library() {
    log_info "Processing VCV Rack library repository..."

    if [ -d "$TARGET_DIR" ]; then
        log_info "Directory '$TARGET_DIR' already exists. Pulling latest changes..."

        if ! (cd "$TARGET_DIR" && git pull); then
            log_error "Failed to update repository"
            return 1
        fi

        log_info "Repository updated successfully"
    else
        log_info "Cloning repository into '$TARGET_DIR'..."

        if ! git clone "$REPO_URL" "$TARGET_DIR"; then
            log_error "Failed to clone repository"
            return 1
        fi

        log_info "Repository cloned successfully"
    fi

    return 0
}

# Function to run data processing
run_data_processing() {
    log_info "Running data processing (parsing manifests and downloading images)..."

    if ! python3 process_data.py; then
        log_error "Data processing failed"
        return 1
    fi

    log_info "Data processing completed successfully"
    return 0
}

# Function to generate search file
generate_search_file() {
    log_info "Generating search file..."

    if ! python3 generate_search_file.py; then
        log_error "Search file generation failed"
        return 1
    fi

    log_info "Search file generated successfully"
    return 0
}

# Function to deploy files to site directory
deploy_files() {
    log_info "Deploying files to site directory..."

    # Create site directory structure
    if ! mkdir -p "$SITE_DIR/images"; then
        log_error "Failed to create site directory structure"
        return 1
    fi

    # Copy main files
    if ! cp index.html "$SITE_DIR/"; then
        log_error "Failed to copy index.html"
        return 1
    fi
    log_info "Copied index.html to site/"

    if ! cp search_file.json "$SITE_DIR/"; then
        log_error "Failed to copy search_file.json"
        return 1
    fi
    log_info "Copied search_file.json to site/"

    if ! cp fuzzy.js "$SITE_DIR/"; then
        log_error "Failed to copy fuzzy.js"
        return 1
    fi
    log_info "Copied fuzzy.js to site/"

    # Copy cache images to site
    if [ -d "$CACHE_DIR" ]; then
        if ! cp -r "$CACHE_DIR/." "$SITE_DIR/images/"; then
            log_error "Failed to copy cached images"
            return 1
        fi
        log_info "Copied cached images to site/images/"
    else
        log_warn "Cache directory not found, skipping image copy"
    fi

    return 0
}

# Function to clean up build artifacts
cleanup_build() {
    log_info "Cleaning up build artifacts..."

    # Remove temporary files if they exist
    if [ -f "parsed_plugins.json" ]; then
        rm -f "parsed_plugins.json"
        log_info "Removed parsed_plugins.json"
    fi

    return 0
}

# Function to validate build output
validate_build() {
    log_info "Validating build output..."

    # Check if required files exist
    if [ ! -f "$SITE_DIR/index.html" ]; then
        log_error "Missing index.html in site directory"
        return 1
    fi

    if [ ! -f "$SITE_DIR/search_file.json" ]; then
        log_error "Missing search_file.json in site directory"
        return 1
    fi

    if [ ! -d "$SITE_DIR/images" ]; then
        log_error "Missing images directory in site directory"
        return 1
    fi

    # Check if search file is valid JSON
    if ! python3 -c "import json; json.load(open('$SITE_DIR/search_file.json'))" &> /dev/null; then
        log_error "Invalid JSON in search_file.json"
        return 1
    fi

    log_info "Build validation completed successfully"
    return 0
}

# Function to display build summary
display_build_summary() {
    log_info "Build Summary:"
    log_info "=============="

    if [ -f "$SITE_DIR/search_file.json" ]; then
        local module_count=$(python3 -c "import json; data=json.load(open('$SITE_DIR/search_file.json')); print(len(data['data']))" 2>/dev/null || echo "Unknown")
        log_info "Total modules processed: $module_count"
    fi

    if [ -d "$SITE_DIR/images" ]; then
        local image_count=$(find "$SITE_DIR/images" -name "*.webp" 2>/dev/null | wc -l)
        log_info "Total images cached: $image_count"
    fi

    local site_size=$(du -sh "$SITE_DIR" 2>/dev/null | cut -f1 || echo "Unknown")
    log_info "Site directory size: $site_size"

    log_info "Site files are ready in the '$SITE_DIR' directory"
}