"""
Unit tests for utility functions.
"""

import pytest
from scripts.utils import (
    get_environment,
    generate_snapshot_id,
    validate_snapshot_metadata
)


def test_get_environment_default():
    """Test default environment."""
    env = get_environment()
    assert env == 'dev'


def test_generate_snapshot_id():
    """Test snapshot ID generation."""
    run_id = "12345"
    job_name = "default"
    snapshot_id = generate_snapshot_id(run_id, job_name)
    
    assert snapshot_id.startswith("snapshot-")
    assert job_name in snapshot_id
    assert run_id in snapshot_id


def test_validate_snapshot_metadata_valid():
    """Test valid snapshot metadata."""
    metadata = {
        'global_entity_id': 'snapshot-001',
        'timestamp': '2024-01-01T00:00:00Z',
        'pipeline_version': '1.0.0',
        'model_version': '1.0.0',
        'snapshot_type': 'client'
    }
    
    assert validate_snapshot_metadata(metadata) is True


def test_validate_snapshot_metadata_invalid():
    """Test invalid snapshot metadata."""
    metadata = {
        'global_entity_id': 'snapshot-001',
        'timestamp': '2024-01-01T00:00:00Z',
        # Missing required fields
    }
    
    assert validate_snapshot_metadata(metadata) is False

