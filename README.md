# VMT Actuarial Modeling Databricks Pipeline

This repository contains the infrastructure and automation for running actuarial modeling pipelines on Databricks using **Databricks Asset Bundles**.

## Overview

This pipeline enables actuaries to:
- Experiment safely using feature branches and PR-gated workflows
- Promote immutable, versioned releases (SemVer) for production
- Run environment-agnostic code across Dev, Stage, and Prod
- Manage Databricks jobs via **Databricks Asset Bundles** (YAML-based)
- Support notebook replacement and fallback for controlled deviations
- **Toggle between Serverless and Cluster compute** per run via GitHub workflows
- **Use GitHub release tags** to tie Databricks runs to specific asset versions

## Repository Structure

```
.
├── databricks.yml          # Root Databricks Asset Bundle configuration
├── resources/              # Asset Bundle resources
│   └── jobs/               # Job definitions
│       ├── default-serverless.yml  # Default pipeline (Serverless)
│       ├── default-cluster.yml     # Default pipeline (Cluster)
│       ├── centene-serverless.yml  # Centene pipeline (Serverless)
│       └── centene-cluster.yml     # Centene pipeline (Cluster)
├── .databricks/           # Databricks bundle state (auto-generated)
├── .github/
│   └── workflows/          # GitHub Actions workflows
│       ├── lint.yml        # Linting and formatting
│       ├── test.yml        # Unit tests
│       ├── run_pipeline.yml # Run Databricks pipeline
│       ├── pr_validation.yml # PR validation
│       ├── promote.yml     # Promotion workflow
│       └── cleanup.yml     # Cleanup failed runs
├── scripts/                # Python helper scripts
│   ├── create_new_job.py  # Create new job from template
│   ├── utils.py           # Utility functions
│   ├── logger.py          # Structured logging
│   ├── validate_job_definitions.py
│   ├── validate_job_model_alignment.py
│   ├── cleanup_failed_runs.py
│   └── update_vmt_datastore.py
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
└── .pre-commit-config.yaml # Pre-commit hooks
```

## Getting Started

### Prerequisites

- Python 3.10+
- Terraform >= 1.0
- Databricks CLI
- GitHub Actions (for CI/CD)

### Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

3. **Configure Terraform:**
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   ```

4. **Initialize Terraform:**
   ```bash
   terraform init
   ```

### Creating a New Job

To create a new pipeline job based on the default template:

```bash
python scripts/create_new_job.py <job_name> [--base-job default] [--client-entity-id <id>]
```

Example:
```bash
python scripts/create_new_job.py ford --client-entity-id client-ford-001
```

This will create:
- `terraform/jobs/ford/ford_job.yml` - Job configuration
- `terraform/jobs/ford/ford_job.tf` - Terraform reference file
- Placeholder notebook files

## GitHub Workflows

### Run Pipeline

Manually trigger a pipeline run:
1. Go to Actions → Run Databricks Pipeline
2. Select:
   - **Job name** (default, centene, etc.)
   - **Compute type** (serverless or cluster) ⚡
   - **Environment** (dev, qa, stage, prod)
   - **Release tag** (GitHub release tag, defaults to latest)
   - **Model repo tag** (model repository tag/branch)
3. Click "Run workflow"

The workflow will:
- Deploy the bundle with the specified release tag
- Run the selected job with the chosen compute type
- Databricks handles asset transfers automatically

### Deploy Bundle

Deploy the bundle to an environment:
1. Go to Actions → Deploy Databricks Bundle
2. Select environment, release tag, and model repo tag
3. Click "Run workflow"

### Create Release

Create a new release and optionally deploy:
1. Go to Actions → Create Release and Deploy Bundle
2. Enter version (e.g., 1.0.0)
3. Select target environment
4. Click "Run workflow"

This will:
- Create a Git tag (v1.0.0)
- Create a GitHub release
- Optionally deploy the bundle to the target environment

### PR Validation

Automatically runs on pull requests:
- Linting and formatting checks
- Databricks bundle validation
- Job definition validation
- Smoke tests

## Job Configuration

Jobs are defined in YAML files under `resources/jobs/`. Each job has two versions:
- `<job_name>-serverless.yml` - Serverless compute
- `<job_name>-cluster.yml` - Traditional cluster compute

Example structure:
```yaml
# resources/jobs/default-serverless.yml
resources:
  jobs:
    default_serverless:
      name: "Default Actuarial Pipeline (Serverless)"
      tags:
        global_entity_id: "pipeline-default-v1.0.0"
        compute_type: "serverless"
      tasks:
        - task_key: step_1_data_ingest
          notebook_task:
            notebook_path: "${var.model_repo_path}/notebooks/default/step_1_data_ingest"
          compute_key: "serverless-compute"
```

### Toggling Compute Types

You can run the same job with different compute types:
- **Serverless**: Fast startup, automatic scaling, pay-per-use
- **Cluster**: Full control, predictable performance, fixed costs

Toggle via GitHub workflow input or use the helper script:
```bash
./scripts/run_pipeline.sh default serverless dev v1.0.0 main
./scripts/run_pipeline.sh default cluster prod v1.0.0 main
```

### Release Tag Integration

GitHub release tags are automatically passed to jobs:
- `github_release_tag` - The GitHub release tag (e.g., v1.0.0)
- `model_repo_tag` - The model repository tag/branch
- These are available as notebook parameters for traceability

## Environment Variables

### Required GitHub Secrets:
- `DATABRICKS_HOST` - Databricks workspace URL
- `DATABRICKS_TOKEN` - Databricks personal access token
- `DATABRICKS_HOST_DEV`, `DATABRICKS_TOKEN_DEV` - Dev environment
- `DATABRICKS_HOST_QA`, `DATABRICKS_TOKEN_QA` - QA environment
- `DATABRICKS_HOST_STAGE`, `DATABRICKS_TOKEN_STAGE` - Stage environment
- `DATABRICKS_HOST_PROD`, `DATABRICKS_TOKEN_PROD` - Prod environment

### Required GitHub Variables:
- `MODEL_REPO_ORG` - Model repository organization
- `MODEL_REPO_NAME` - Model repository name

### Bundle Variables (set in workflows):
- `GITHUB_REPOSITORY_URL` - Auto-set by GitHub Actions
- `GITHUB_REF_NAME` - Auto-set by GitHub Actions
- `GITHUB_RUN_ID` - Auto-set by GitHub Actions
- `GITHUB_RELEASE_TAG` - Set from release tag or workflow input
- `MODEL_REPO_TAG` - Set from workflow input (defaults to "main")

## Development

### Running Tests

```bash
pytest tests/ --cov=scripts
```

### Linting

```bash
black .
ruff check .
isort .
```

### Validating Bundle

```bash
# Validate bundle configuration
databricks bundle validate -t dev

# Or use the helper script
python scripts/validate_bundle.py --environment dev
```

### Running Jobs Locally

```bash
# Run with serverless compute
databricks bundle run default_serverless -t dev

# Run with cluster compute
databricks bundle run default_cluster -t dev

# Or use the helper script
./scripts/run_pipeline.sh default serverless dev v1.0.0 main
```

## Documentation

See `Plan.md` for detailed architecture and design decisions.

## License

[Your License Here]

