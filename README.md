# VMT Actuarial Modeling Databricks Pipeline

This repository contains the infrastructure and automation for running actuarial modeling pipelines on Databricks.

## Overview

This pipeline enables actuaries to:
- Experiment safely using feature branches and PR-gated workflows
- Promote immutable, versioned releases (SemVer) for production
- Run environment-agnostic code across Dev, Stage, and Prod
- Manage Databricks jobs via Terraform as the single source of truth
- Support notebook replacement and fallback for controlled deviations

## Repository Structure

```
.
├── terraform/              # Terraform configurations
│   ├── main.tf             # Main Terraform configuration
│   ├── variables.tf        # Variable definitions
│   ├── modules/            # Reusable Terraform modules
│   │   └── pipeline/       # Pipeline job module
│   └── jobs/               # Job definitions
│       ├── default/        # Gold standard pipeline
│       ├── ford/           # Ford-specific pipeline
│       └── centene/        # Centene-specific pipeline
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
2. Select job name, environment, and model tag
3. Click "Run workflow"

### PR Validation

Automatically runs on pull requests:
- Linting and formatting checks
- Terraform validation
- Job definition validation
- Smoke tests

### Promotion

Promote a pipeline or model to production:
1. Go to Actions → Promote Pipeline/Model
2. Select promotion type, version, and environment
3. Choose auto-apply option

## Job Configuration

Jobs are defined in YAML files under `terraform/jobs/<job_name>/<job_name>_job.yml`.

Example structure:
```yaml
name: "Default Actuarial Pipeline"
global_entity_id: "pipeline-default-v1.0.0"
version: "1.0.0"
client_specific: false
notebooks:
  - name: "step_1_data_ingest"
    path: "/Repos/${MODEL_REPO}/notebooks/default/step_1_data_ingest"
    description: "Import and clean data"
```

## Environment Variables

Required secrets in GitHub:
- `DATABRICKS_HOST` - Databricks workspace URL
- `DATABRICKS_TOKEN` - Databricks personal access token
- `MODEL_REPO_ORG` - Model repository organization
- `MODEL_REPO_NAME` - Model repository name
- `MODEL_REPO_TOKEN` - Token for accessing model repository

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

### Validating Job Definitions

```bash
python scripts/validate_job_definitions.py
```

## Documentation

See `Plan.md` for detailed architecture and design decisions.

## License

[Your License Here]

