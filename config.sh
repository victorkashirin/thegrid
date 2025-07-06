#!/bin/bash

# Configuration for VCV Rack Module Search Build Scripts
# This file contains all configuration variables used by the build system

# Repository configuration
REPO_URL="https://github.com/VCVRack/library.git"

# Directory configuration
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

# Build configuration
BUILD_PARALLEL=true
BUILD_VERBOSE=false

# Exit on error by default
set -e