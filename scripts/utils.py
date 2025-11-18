"""
Utility functions for pipeline operations.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


def get_environment() -> str:
    """Get the current environment from environment variable."""
    return os.getenv('ENVIRONMENT', 'dev').lower()


def generate_snapshot_id(run_id: str, job_name: str) -> str:
    """Generate a unique snapshot ID for a pipeline run."""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    return f"snapshot-{job_name}-{run_id}-{timestamp}"


def load_notebook_params() -> Dict[str, Any]:
    """Load notebook parameters from Databricks widget values or environment."""
    try:
        # Try to get from Databricks widgets
        import dbutils
        params = {}
        for param in ['env', 'snapshot_id', 'run_id', 'job_name', 'notebook_base_path']:
            try:
                params[param] = dbutils.widgets.get(param)
            except:
                params[param] = os.getenv(param.upper(), '')
        return params
    except:
        # Fallback to environment variables
        return {
            'env': get_environment(),
            'snapshot_id': os.getenv('SNAPSHOT_ID', ''),
            'run_id': os.getenv('RUN_ID', ''),
            'job_name': os.getenv('JOB_NAME', ''),
            'notebook_base_path': os.getenv('NOTEBOOK_BASE_PATH', '')
        }


def save_state_to_db(state: Dict[str, Any], snapshot_id: str, connection_string: str):
    """
    Save state to database for large state objects.
    For small state, use notebook parameters instead.
    """
    # This would be implemented with actual database connection
    # Example using SQLAlchemy or similar
    pass


def get_state_from_db(snapshot_id: str, connection_string: str) -> Optional[Dict[str, Any]]:
    """Retrieve state from database."""
    # This would be implemented with actual database connection
    pass


def validate_snapshot_metadata(metadata: Dict[str, Any]) -> bool:
    """Validate that snapshot metadata contains all required fields."""
    required_fields = [
        'global_entity_id',
        'timestamp',
        'pipeline_version',
        'model_version',
        'snapshot_type'
    ]
    
    return all(field in metadata for field in required_fields)


def format_event_data(event_type: str, data: Dict[str, Any], event_id: int) -> Dict[str, Any]:
    """
    Format data for Azure Event Hub using CloudEvents format.
    Returns structured event data.
    """
    return {
        'event_id': event_id,
        'event_type': event_type,
        'source': 'databricks-pipeline',
        'specversion': '1.0',
        'time': datetime.utcnow().isoformat() + 'Z',
        'data': data
    }

