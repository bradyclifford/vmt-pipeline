#!/usr/bin/env python3
"""
Script to create a new Databricks job based on the default job template.
This allows actuaries to create feature branches for testing new pipeline configurations.
"""

import argparse
import os
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any


def load_yaml_config(file_path: Path) -> Dict[str, Any]:
    """Load and parse a YAML configuration file."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def save_yaml_config(file_path: Path, config: Dict[str, Any]):
    """Save a configuration dictionary to a YAML file."""
    with open(file_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def create_new_job(job_name: str, base_job: str = "default", client_entity_id: str = None):
    """
    Create a new job configuration based on an existing job.
    
    Args:
        job_name: Name of the new job (e.g., 'ford', 'centene')
        base_job: Name of the base job to copy from (default: 'default')
        client_entity_id: Optional client entity ID if this is client-specific
    """
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    terraform_dir = repo_root / "terraform" / "jobs"
    
    # Source and destination paths
    source_dir = terraform_dir / base_job
    dest_dir = terraform_dir / job_name
    
    if dest_dir.exists():
        raise ValueError(f"Job '{job_name}' already exists at {dest_dir}")
    
    if not source_dir.exists():
        raise ValueError(f"Base job '{base_job}' not found at {source_dir}")
    
    # Create destination directory
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Load base job configuration
    base_config_path = source_dir / f"{base_job}_job.yml"
    if not base_config_path.exists():
        raise ValueError(f"Base job config not found: {base_config_path}")
    
    config = load_yaml_config(base_config_path)
    
    # Modify configuration for new job
    config['name'] = f"{job_name.title()} Actuarial Pipeline"
    config['global_entity_id'] = f"pipeline-{job_name}-v{config.get('version', '1.0.0')}"
    config['fallback_job'] = base_job
    
    if client_entity_id:
        config['client_specific'] = True
        config['client_entity_id'] = client_entity_id
    else:
        config['client_specific'] = False
        config['client_entity_id'] = None
    
    # Save new configuration
    new_config_path = dest_dir / f"{job_name}_job.yml"
    save_yaml_config(new_config_path, config)
    
    # Copy Terraform file template
    tf_template = dest_dir / f"{job_name}_job.tf"
    tf_template.write_text(
        f"# This file is kept for reference but the actual job is defined in main.tf\n"
        f"# The job configuration is loaded from {job_name}_job.yml\n"
    )
    
    # Create placeholder notebook files (empty, for Terraform reference)
    notebooks_dir = dest_dir
    for notebook in config.get('notebooks', []):
        notebook_name = notebook.get('name', '').replace('_', '-')
        notebook_path = notebooks_dir / f"{notebook_name}.ipynb"
        if not notebook_path.exists():
            # Create empty notebook JSON structure
            empty_notebook = {
                "cells": [
                    {
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": [
                            f"# {notebook.get('description', notebook_name)}\n",
                            f"\n",
                            f"This notebook will be replaced by the actual notebook from the model repository."
                        ]
                    }
                ],
                "metadata": {
                    "kernelspec": {
                        "display_name": "Python 3",
                        "language": "python",
                        "name": "python3"
                    }
                },
                "nbformat": 4,
                "nbformat_minor": 4
            }
            import json
            with open(notebook_path, 'w') as f:
                json.dump(empty_notebook, f, indent=2)
    
    print(f"✅ Created new job '{job_name}' at {dest_dir}")
    print(f"   Configuration: {new_config_path}")
    print(f"   Base job: {base_job}")
    if client_entity_id:
        print(f"   Client Entity ID: {client_entity_id}")
    print(f"\nNext steps:")
    print(f"1. Review and modify {new_config_path}")
    print(f"2. Update terraform/main.tf to include the new job module")
    print(f"3. Commit changes to a feature branch")


def main():
    parser = argparse.ArgumentParser(
        description="Create a new Databricks job based on a template"
    )
    parser.add_argument(
        'job_name',
        help='Name of the new job (e.g., ford, centene)'
    )
    parser.add_argument(
        '--base-job',
        default='default',
        help='Base job to copy from (default: default)'
    )
    parser.add_argument(
        '--client-entity-id',
        help='Client entity ID if this is a client-specific job'
    )
    
    args = parser.parse_args()
    
    try:
        create_new_job(
            job_name=args.job_name,
            base_job=args.base_job,
            client_entity_id=args.client_entity_id
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

