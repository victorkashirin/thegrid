"""
Custom exceptions for VCV Rack Module Search.

This module defines custom exception classes for different error types
to replace silent failures with proper error handling.
"""

from typing import Optional


class VCVModuleSearchError(Exception):
    """Base exception for all VCV Module Search errors."""
    pass


class NetworkError(VCVModuleSearchError):
    """Exception raised for network-related errors."""
    
    def __init__(self, message: str, url: Optional[str] = None, status_code: Optional[int] = None):
        self.url = url
        self.status_code = status_code
        super().__init__(message)
    
    def __str__(self):
        base_message = super().__str__()
        if self.url:
            base_message += f" (URL: {self.url})"
        if self.status_code:
            base_message += f" (Status: {self.status_code})"
        return base_message


class DataParsingError(VCVModuleSearchError):
    """Exception raised for data parsing errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, line_number: Optional[int] = None):
        self.file_path = file_path
        self.line_number = line_number
        super().__init__(message)
    
    def __str__(self):
        base_message = super().__str__()
        if self.file_path:
            base_message += f" (File: {self.file_path})"
        if self.line_number:
            base_message += f" (Line: {self.line_number})"
        return base_message


class FileProcessingError(VCVModuleSearchError):
    """Exception raised for file processing errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None):
        self.file_path = file_path
        super().__init__(message)
    
    def __str__(self):
        base_message = super().__str__()
        if self.file_path:
            base_message += f" (File: {self.file_path})"
        return base_message


class ImageProcessingError(VCVModuleSearchError):
    """Exception raised for image processing errors."""
    
    def __init__(self, message: str, image_path: Optional[str] = None):
        self.image_path = image_path
        super().__init__(message)
    
    def __str__(self):
        base_message = super().__str__()
        if self.image_path:
            base_message += f" (Image: {self.image_path})"
        return base_message


class ConfigurationError(VCVModuleSearchError):
    """Exception raised for configuration-related errors."""
    pass


class ValidationError(VCVModuleSearchError):
    """Exception raised for data validation errors."""
    
    def __init__(self, message: str, field_name: Optional[str] = None, field_value: Optional[str] = None):
        self.field_name = field_name
        self.field_value = field_value
        super().__init__(message)
    
    def __str__(self):
        base_message = super().__str__()
        if self.field_name:
            base_message += f" (Field: {self.field_name})"
        if self.field_value:
            base_message += f" (Value: {self.field_value})"
        return base_message


class GitOperationError(VCVModuleSearchError):
    """Exception raised for git operation errors."""
    
    def __init__(self, message: str, command: Optional[str] = None, return_code: Optional[int] = None):
        self.command = command
        self.return_code = return_code
        super().__init__(message)
    
    def __str__(self):
        base_message = super().__str__()
        if self.command:
            base_message += f" (Command: {self.command})"
        if self.return_code:
            base_message += f" (Return code: {self.return_code})"
        return base_message