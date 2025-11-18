#!/usr/bin/env python3
"""
Update VMT Data Store with new pipeline/model versions after promotion.
This script updates the VMT Data Store to make new pipelines/models available in the UI.
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import Dict, Any


def load_job_config(terraform_dir: Path, job_name: str) -> Dict[str, Any]:
    """Load job configuration from YAML file."""
    job_yml = terraform_dir / "jobs" / job_name / f"{job_name}_job.yml"
    
    if not job_yml.exists():
        raise FileNotFoundError(f"Job config not found: {job_yml}")
    
    with open(job_yml, 'r') as f:
        return yaml.safe_load(f)


def update_vmt_datastore(
    promotion_type: str,
    version: str,
    environment: str,
    terraform_dir: Path = None
):
    """
    Update VMT Data Store with promotion information.
    
    In a real implementation, this would:
    1. Connect to the VMT Data Store (SQL database)
    2. Insert/update pipeline or model records
    3. Make them available for selection in the UI
    """
    if terraform_dir is None:
        terraform_dir = Path(__file__).parent.parent / "terraform"
    
    print(f"Updating VMT Data Store...")
    print(f"  Promotion Type: {promotion_type}")
    print(f"  Version: {version}")
    print(f"  Environment: {environment}")
    
    if promotion_type in ['pipeline', 'both']:
        # Load all job configurations
        jobs_dir = terraform_dir / "jobs"
        for job_dir in jobs_dir.iterdir():
            if not job_dir.is_dir():
                continue
            
            job_name = job_dir.name
            try:
                job_config = load_job_config(terraform_dir, job_name)
                
                print(f"\n  Pipeline: {job_config['name']}")
                print(f"    Global Entity ID: {job_config['global_entity_id']}")
                print(f"    Client Specific: {job_config.get('client_specific', False)}")
                
                # In real implementation, insert into database:
                # INSERT INTO pipelines (global_entity_id, name, version, environment, ...)
                # VALUES (...)
                
            except Exception as e:
                print(f"  ⚠️  Error loading job {job_name}: {e}")
    
    if promotion_type in ['model', 'both']:
        print(f"\n  Model promotion would update model repository records")
        # In real implementation, this would update model records from model repo
    
    print("\n✅ VMT Data Store update complete (simulated)")


def main():
    parser = argparse.ArgumentParser(description="Update VMT Data Store after promotion")
    parser.add_argument('--promotion-type', required=True, choices=['pipeline', 'model', 'both'])
    parser.add_argument('--version', required=True, help='SemVer version')
    parser.add_argument('--environment', required=True, help='Target environment')
    parser.add_argument('--terraform-dir', type=Path, help='Path to terraform directory')
    
    args = parser.parse_args()
    
    try:
        update_vmt_datastore(
            promotion_type=args.promotion_type,
            version=args.version,
            environment=args.environment,
            terraform_dir=args.terraform_dir
        )
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

