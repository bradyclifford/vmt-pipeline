#!/bin/bash
# Helper script to run Databricks pipeline jobs
# Usage: ./scripts/run_pipeline.sh <job_name> <compute_type> <environment> [release_tag] [model_repo_tag]

set -e

JOB_NAME=$1
COMPUTE_TYPE=$2
ENVIRONMENT=$3
RELEASE_TAG=${4:-"latest"}
MODEL_REPO_TAG=${5:-"main"}

if [ -z "$JOB_NAME" ] || [ -z "$COMPUTE_TYPE" ] || [ -z "$ENVIRONMENT" ]; then
    echo "Usage: $0 <job_name> <compute_type> <environment> [release_tag] [model_repo_tag]"
    echo "  job_name: default, centene, etc."
    echo "  compute_type: serverless or cluster"
    echo "  environment: dev, qa, stage, prod"
    echo "  release_tag: GitHub release tag (default: latest)"
    echo "  model_repo_tag: Model repo tag/branch (default: main)"
    exit 1
fi

FULL_JOB_NAME="${JOB_NAME}_${COMPUTE_TYPE}"

echo "Running Databricks pipeline:"
echo "  Job: ${FULL_JOB_NAME}"
echo "  Environment: ${ENVIRONMENT}"
echo "  Release Tag: ${RELEASE_TAG}"
echo "  Model Repo Tag: ${MODEL_REPO_TAG}"

# Export variables for databricks bundle
export GITHUB_RELEASE_TAG="${RELEASE_TAG}"
export MODEL_REPO_TAG="${MODEL_REPO_TAG}"

# Run the job
databricks bundle run "${FULL_JOB_NAME}" -t "${ENVIRONMENT}"

echo "✅ Job completed successfully"

