#!/usr/bin/env python3
"""
Validate that job definitions align with model definitions.
Checks that notebooks referenced in jobs exist in the model repository.
"""

import argparse
import sys
from pathlib import Path
import yaml


def load_job_configs(terraform_dir: Path) -> dict:
    """Load all job configurations from YAML files."""
    jobs = {}
    jobs_dir = terraform_dir / "jobs"
    
    for job_dir in jobs_dir.iterdir():
        if not job_dir.is_dir():
            continue
        
        yml_files = list(job_dir.glob("*_job.yml"))
        for yml_file in yml_files:
            with open(yml_file, 'r') as f:
                config = yaml.safe_load(f)
                job_name = job_dir.name
                jobs[job_name] = config
    
    return jobs


def check_model_alignment(job_config: dict, model_repo_path: Path) -> list[str]:
    """Check if notebooks in job config exist in model repo."""
    errors = []
    job_name = job_config.get('name', 'unknown')
    
    # Determine which model folder to check
    # This assumes the job name matches the model folder name
    # In practice, this would be more sophisticated
    model_folder = job_config.get('model_folder', job_name)
    model_dir = model_repo_path / "notebooks" / model_folder
    
    if not model_dir.exists():
        errors.append(f"Model directory not found: {model_dir}")
        return errors
    
    # Check each notebook
    for notebook in job_config.get('notebooks', []):
        notebook_name = notebook.get('name', '')
        # Convert notebook name to file name (e.g., step_1_data_ingest -> step_1_data_ingest.ipynb)
        notebook_file = model_dir / f"{notebook_name}.ipynb"
        
        if not notebook_file.exists():
            fallback_to = notebook.get('fallback_to')
            if fallback_to:
                # Check fallback location
                fallback_dir = model_repo_path / "notebooks" / fallback_to
                fallback_file = fallback_dir / f"{notebook_name}.ipynb"
                if not fallback_file.exists():
                    errors.append(
                        f"Notebook '{notebook_name}' not found in model or fallback location"
                    )
            else:
                errors.append(f"Notebook '{notebook_name}' not found in model directory")
    
    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Validate job-model alignment"
    )
    parser.add_argument(
        '--terraform-dir',
        type=Path,
        default=Path(__file__).parent.parent / "terraform",
        help='Path to terraform directory'
    )
    parser.add_argument(
        '--model-repo-path',
        type=Path,
        help='Path to model repository (optional, for local validation)'
    )
    
    args = parser.parse_args()
    
    if not args.terraform_dir.exists():
        print(f"❌ Terraform directory not found: {args.terraform_dir}")
        return 1
    
    jobs = load_job_configs(args.terraform_dir)
    
    if not args.model_repo_path:
        print("⚠️  Model repository path not provided, skipping notebook existence checks")
        print("   This check should be run in CI with access to model repository")
        return 0
    
    if not args.model_repo_path.exists():
        print(f"❌ Model repository path not found: {args.model_repo_path}")
        return 1
    
    all_valid = True
    
    for job_name, job_config in jobs.items():
        print(f"Validating alignment for job: {job_name}...")
        errors = check_model_alignment(job_config, args.model_repo_path)
        
        if errors:
            print(f"  ❌ Errors found:")
            for error in errors:
                print(f"    - {error}")
            all_valid = False
        else:
            print(f"  ✅ Aligned")
    
    if all_valid:
        print("\n✅ All jobs are aligned with models")
        return 0
    else:
        print("\n❌ Some jobs have alignment issues")
        return 1


if __name__ == '__main__':
    sys.exit(main())

