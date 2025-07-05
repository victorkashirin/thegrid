#!/bin/bash

# VCV Rack Module Search Build Script
# This script builds the complete module search system using modular functions

# Source configuration and functions
source "$(dirname "$0")/config.sh"
source "$(dirname "$0")/build_functions.sh"

# Main build function
main() {
    log_info "Starting VCV Rack Module Search build process..."
    
    # Execute build pipeline
    if ! setup_environment; then
        log_error "Environment setup failed"
        exit 1
    fi
    
    if ! clone_or_update_library; then
        log_error "Library repository operation failed"
        exit 1
    fi
    
    if ! run_data_processing; then
        log_error "Data processing failed"
        exit 1
    fi
    
    if ! generate_search_file; then
        log_error "Search file generation failed"
        exit 1
    fi
    
    if ! deploy_files; then
        log_error "File deployment failed"
        exit 1
    fi
    
    if ! validate_build; then
        log_error "Build validation failed"
        exit 1
    fi
    
    # Optional cleanup
    cleanup_build
    
    # Display summary
    display_build_summary
    
    log_info "Build process completed successfully!"
}

# Function to display usage information
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Build the VCV Rack Module Search system"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -v, --verbose  Enable verbose output"
    echo "  --no-cleanup   Skip cleanup of build artifacts"
    echo "  --validate     Only run validation without building"
    echo ""
    echo "Environment Variables:"
    echo "  BUILD_PARALLEL   Enable parallel processing (default: true)"
    echo "  BUILD_VERBOSE    Enable verbose output (default: false)"
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -v|--verbose)
                BUILD_VERBOSE=true
                shift
                ;;
            --no-cleanup)
                SKIP_CLEANUP=true
                shift
                ;;
            --validate)
                VALIDATE_ONLY=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Main execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Parse arguments
    parse_arguments "$@"
    
    # Handle special modes
    if [[ "${VALIDATE_ONLY:-false}" == "true" ]]; then
        log_info "Running validation only..."
        validate_build
        exit $?
    fi
    
    # Override cleanup if requested
    if [[ "${SKIP_CLEANUP:-false}" == "true" ]]; then
        cleanup_build() {
            log_info "Skipping cleanup (--no-cleanup specified)"
            return 0
        }
    fi
    
    # Run main build
    main
fi