#!/usr/bin/env python3
"""
Validate YAML job definition files for correctness and completeness.
"""

import argparse
import sys
from pathlib import Path
import yaml
import jsonschema


# JSON Schema for job definition validation
JOB_SCHEMA = {
    "type": "object",
    "required": ["name", "global_entity_id", "version", "notebooks"],
    "properties": {
        "name": {"type": "string"},
        "global_entity_id": {"type": "string"},
        "version": {"type": "string"},
        "description": {"type": "string"},
        "max_concurrent_runs": {"type": "integer", "minimum": 1},
        "timeout_seconds": {"type": "integer", "minimum": 1},
        "max_retries": {"type": "integer", "minimum": 0},
        "min_retry_interval_millis": {"type": "integer", "minimum": 0},
        "task_timeout_seconds": {"type": "integer", "minimum": 1},
        "client_specific": {"type": "boolean"},
        "client_entity_id": {"type": ["string", "null"]},
        "fallback_job": {"type": ["string", "null"]},
        "notebooks": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["name", "path"],
                "properties": {
                    "name": {"type": "string"},
                    "path": {"type": "string"},
                    "description": {"type": "string"},
                    "fallback_to": {"type": ["string", "null"]}
                }
            }
        },
        "schedule": {
            "type": ["object", "null"],
            "properties": {
                "quartz_cron_expression": {"type": "string"},
                "timezone_id": {"type": "string"},
                "pause_status": {"type": "string", "enum": ["PAUSED", "UNPAUSED"]}
            }
        }
    }
}


def validate_job_file(file_path: Path) -> tuple[bool, list[str]]:
    """Validate a single job YAML file."""
    errors = []
    
    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate against schema
        try:
            jsonschema.validate(instance=config, schema=JOB_SCHEMA)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
        
        # Additional custom validations
        if config.get('client_specific') and not config.get('client_entity_id'):
            errors.append("client_specific is true but client_entity_id is missing")
        
        # Validate notebook paths contain placeholder
        for notebook in config.get('notebooks', []):
            if '${MODEL_REPO}' not in notebook.get('path', ''):
                errors.append(
                    f"Notebook path '{notebook.get('path')}' must contain ${{MODEL_REPO}} placeholder"
                )
        
        return len(errors) == 0, errors
        
    except yaml.YAMLError as e:
        return False, [f"YAML parsing error: {e}"]
    except Exception as e:
        return False, [f"Unexpected error: {e}"]


def validate_all_jobs(terraform_dir: Path) -> bool:
    """Validate all job definition files in the terraform/jobs directory."""
    jobs_dir = terraform_dir / "jobs"
    
    if not jobs_dir.exists():
        print(f"❌ Jobs directory not found: {jobs_dir}")
        return False
    
    all_valid = True
    
    for job_dir in jobs_dir.iterdir():
        if not job_dir.is_dir():
            continue
        
        yml_files = list(job_dir.glob("*_job.yml"))
        if not yml_files:
            print(f"⚠️  No job YAML files found in {job_dir}")
            continue
        
        for yml_file in yml_files:
            print(f"Validating {yml_file}...")
            is_valid, errors = validate_job_file(yml_file)
            
            if is_valid:
                print(f"  ✅ Valid")
            else:
                print(f"  ❌ Invalid:")
                for error in errors:
                    print(f"    - {error}")
                all_valid = False
    
    return all_valid


def main():
    parser = argparse.ArgumentParser(description="Validate job definition YAML files")
    parser.add_argument(
        '--terraform-dir',
        type=Path,
        default=Path(__file__).parent.parent / "terraform",
        help='Path to terraform directory'
    )
    
    args = parser.parse_args()
    
    if not args.terraform_dir.exists():
        print(f"❌ Terraform directory not found: {args.terraform_dir}")
        return 1
    
    is_valid = validate_all_jobs(args.terraform_dir)
    
    if is_valid:
        print("\n✅ All job definitions are valid")
        return 0
    else:
        print("\n❌ Some job definitions have errors")
        return 1


if __name__ == '__main__':
    sys.exit(main())

