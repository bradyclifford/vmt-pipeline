#!/usr/bin/env python3
"""
Cleanup script for failed Databricks job runs.
Removes temporary data and notebooks for failed runs older than specified days.
"""

import argparse
import sys
from datetime import datetime, timedelta
import requests
from typing import List, Dict


def get_failed_runs(
    databricks_host: str,
    databricks_token: str,
    days_old: int,
    job_ids: List[int] = None
) -> List[Dict]:
    """Get list of failed runs older than specified days."""
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    cutoff_timestamp = int(cutoff_date.timestamp() * 1000)
    
    failed_runs = []
    
    # Get all jobs if job_ids not specified
    if not job_ids:
        jobs_response = requests.get(
            f"{databricks_host}/api/2.1/jobs/list",
            headers={"Authorization": f"Bearer {databricks_token}"}
        )
        jobs_response.raise_for_status()
        job_ids = [job['job_id'] for job in jobs_response.json().get('jobs', [])]
    
    # Get runs for each job
    for job_id in job_ids:
        runs_response = requests.get(
            f"{databricks_host}/api/2.1/jobs/runs/list",
            headers={"Authorization": f"Bearer {databricks_token}"},
            params={"job_id": job_id, "limit": 100}
        )
        runs_response.raise_for_status()
        
        runs = runs_response.json().get('runs', [])
        for run in runs:
            # Check if run is failed and older than cutoff
            if (run.get('state', {}).get('result_state') == 'FAILED' and
                run.get('start_time', 0) < cutoff_timestamp):
                failed_runs.append(run)
    
    return failed_runs


def cleanup_run_data(
    databricks_host: str,
    databricks_token: str,
    run_id: int,
    dry_run: bool = True
) -> bool:
    """Cleanup data for a specific run."""
    run_path = f"/tmp/job-{run_id}"
    
    if dry_run:
        print(f"[DRY RUN] Would delete: {run_path}")
        return True
    
    # Delete workspace directory
    delete_response = requests.post(
        f"{databricks_host}/api/2.0/workspace/delete",
        headers={"Authorization": f"Bearer {databricks_token}"},
        json={"path": run_path, "recursive": True}
    )
    
    if delete_response.status_code == 200:
        print(f"✅ Deleted: {run_path}")
        return True
    else:
        print(f"⚠️  Failed to delete {run_path}: {delete_response.text}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Cleanup failed Databricks runs")
    parser.add_argument('--environment', required=True, help='Environment name')
    parser.add_argument('--days-old', type=int, default=7, help='Days old threshold')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--databricks-host', help='Databricks host (or use env var)')
    parser.add_argument('--databricks-token', help='Databricks token (or use env var)')
    
    args = parser.parse_args()
    
    import os
    databricks_host = args.databricks_host or os.getenv('DATABRICKS_HOST')
    databricks_token = args.databricks_token or os.getenv('DATABRICKS_TOKEN')
    
    if not databricks_host or not databricks_token:
        print("❌ Databricks host and token are required")
        return 1
    
    print(f"Searching for failed runs older than {args.days_old} days...")
    failed_runs = get_failed_runs(databricks_host, databricks_token, args.days_old)
    
    print(f"Found {len(failed_runs)} failed runs to cleanup")
    
    if args.dry_run:
        print("\n[DRY RUN MODE - No data will be deleted]")
    
    cleaned = 0
    for run in failed_runs:
        run_id = run['run_id']
        run_name = run.get('run_name', 'unknown')
        start_time = datetime.fromtimestamp(run.get('start_time', 0) / 1000)
        
        print(f"\nProcessing run: {run_name} (ID: {run_id}, Started: {start_time})")
        if cleanup_run_data(databricks_host, databricks_token, run_id, args.dry_run):
            cleaned += 1
    
    print(f"\n✅ Cleaned up {cleaned} runs")
    return 0


if __name__ == '__main__':
    sys.exit(main())

