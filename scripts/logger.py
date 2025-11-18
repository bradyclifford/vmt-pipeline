"""
Structured logging utility for Databricks notebooks with Application Insights integration.
"""

import logging
import os
import sys
from typing import Dict, Any, Optional


class PipelineLogger:
    """Logger configured for Application Insights and structured logging."""
    
    def __init__(self, name: str = __name__, connection_string: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Configure Application Insights if connection string is provided
        if connection_string:
            self._setup_application_insights(connection_string)
        elif os.getenv('APPINSIGHTS_CONNECTION_STRING'):
            self._setup_application_insights(os.getenv('APPINSIGHTS_CONNECTION_STRING'))
        
        # Add console handler if not already present
        if not self.logger.handlers:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def _setup_application_insights(self, connection_string: str):
        """Configure Azure Application Insights logging."""
        try:
            # Install package if not available
            try:
                from azure.monitor.opentelemetry import configure_azure_monitor
            except ImportError:
                import subprocess
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', 
                    'azure-monitor-opentelemetry'
                ])
                from azure.monitor.opentelemetry import configure_azure_monitor
            
            # Configure Application Insights
            configure_azure_monitor(connection_string=connection_string)
            self.logger.info("Application Insights configured successfully")
        except Exception as e:
            self.logger.warning(f"Failed to configure Application Insights: {e}")
    
    def _add_custom_dimensions(
        self, 
        level: str, 
        message: str, 
        event_id: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Add custom dimensions for Application Insights."""
        dimensions = {
            'notebook': os.getenv('NOTEBOOK_NAME', 'unknown'),
            'job_name': os.getenv('JOB_NAME', 'unknown'),
            'run_id': os.getenv('RUN_ID', 'unknown'),
            'environment': os.getenv('ENVIRONMENT', 'unknown'),
            **kwargs
        }
        
        if event_id:
            dimensions['event_id'] = event_id
        
        return dimensions
    
    def info(self, message: str, event_id: Optional[int] = None, **kwargs):
        """Log info message with custom dimensions."""
        extra = {'custom_dimensions': self._add_custom_dimensions('info', message, event_id, **kwargs)}
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, event_id: Optional[int] = None, **kwargs):
        """Log warning message with custom dimensions."""
        extra = {'custom_dimensions': self._add_custom_dimensions('warning', message, event_id, **kwargs)}
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, event_id: Optional[int] = None, **kwargs):
        """Log error message with custom dimensions."""
        extra = {'custom_dimensions': self._add_custom_dimensions('error', message, event_id, **kwargs)}
        self.logger.error(message, extra=extra)
    
    def critical(self, message: str, event_id: Optional[int] = None, **kwargs):
        """Log critical message with custom dimensions."""
        extra = {'custom_dimensions': self._add_custom_dimensions('critical', message, event_id, **kwargs)}
        self.logger.critical(message, extra=extra)


# Global logger instance
_logger: Optional[PipelineLogger] = None


def get_logger(name: str = __name__) -> PipelineLogger:
    """Get or create a global logger instance."""
    global _logger
    if _logger is None:
        _logger = PipelineLogger(name)
    return _logger

