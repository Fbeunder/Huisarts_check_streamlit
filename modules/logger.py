import streamlit as st
import os
from datetime import datetime

class Logger:
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    DEBUG = 'DEBUG'
    
    def __init__(self, data_layer=None):
        self.data_layer = data_layer
        self.level = os.getenv('LOG_LEVEL', 'INFO')
    
    def info(self, message, data=None):
        """Log an info message"""
        self._log(self.INFO, message, data)
    
    def warning(self, message, data=None):
        """Log a warning message"""
        self._log(self.WARNING, message, data)
    
    def error(self, message, data=None):
        """Log an error message"""
        self._log(self.ERROR, message, data)
    
    def debug(self, message, data=None):
        """Log a debug message"""
        self._log(self.DEBUG, message, data)
    
    def _log(self, level, message, data=None):
        """Internal logging method"""
        # Always print to console
        log_entry = f"{datetime.now().isoformat()} [{level}] {message}"
        print(log_entry)
        
        # In the real implementation, this would log to the database
        # For now, just demonstrating the structure
        if self.data_layer and level != self.DEBUG:  # Don't store DEBUG logs
            # Would store log in database here
            pass