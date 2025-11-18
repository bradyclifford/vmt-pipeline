#!/usr/bin/env python3
"""
Validate Databricks Asset Bundle configuration.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def validate_bundle(environment: str = "dev") -> bool:
    """Validate the Databricks bundle configuration."""
    try:
        result = subprocess.run(
            ["databricks", "bundle", "validate", "-t", environment],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Bundle validation failed:", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        return False
    except FileNotFoundError:
        print("❌ Databricks CLI not found. Please install it first.", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Validate Databricks Asset Bundle")
    parser.add_argument(
        '--environment',
        '-t',
        default='dev',
        help='Target environment (default: dev)'
    )
    
    args = parser.parse_args()
    
    success = validate_bundle(args.environment)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

