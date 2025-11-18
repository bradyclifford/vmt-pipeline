"""
Smoke tests for job configurations.
"""

import pytest
from pathlib import Path
import yaml


def test_all_job_ymls_exist():
    """Verify all job YAML files exist and are valid."""
    terraform_dir = Path(__file__).parent.parent.parent / "terraform"
    jobs_dir = terraform_dir / "jobs"
    
    if not jobs_dir.exists():
        pytest.skip("Jobs directory not found")
    
    for job_dir in jobs_dir.iterdir():
        if not job_dir.is_dir():
            continue
        
        yml_files = list(job_dir.glob("*_job.yml"))
        assert len(yml_files) > 0, f"No YAML files found in {job_dir}"
        
        for yml_file in yml_files:
            with open(yml_file, 'r') as f:
                config = yaml.safe_load(f)
                assert config is not None, f"Invalid YAML in {yml_file}"
                assert 'name' in config, f"Missing 'name' in {yml_file}"
                assert 'global_entity_id' in config, f"Missing 'global_entity_id' in {yml_file}"
                assert 'notebooks' in config, f"Missing 'notebooks' in {yml_file}"

